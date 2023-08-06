import os
import tempfile
import uuid

from jaynes.helpers import path_no_ext
from jaynes.constants import JAYNES_PARAMS_KEY


def s3_mount(bucket, prefix, local, remote=None, docker=None, pypath=False):
    with tempfile.NamedTemporaryFile('wb+', suffix='.tar') as tf:
        temp_path = tf.name
    temp_dir = os.path.dirname(temp_path)
    temp_filename = os.path.basename(temp_path)
    remote = remote if remote else path_no_ext(f"/tmp/{temp_filename}")
    docker = docker if docker else remote
    abs_remote = os.path.abspath(remote)
    abs_docker = os.path.abspath(docker)
    local_script = f"""
            pwd &&
            mkdir -p {temp_dir}  && 
            # Do not use absolute path in tar.
            tar czf {temp_path} {local}
            aws s3 cp {temp_path} s3://{bucket}/{prefix}/{temp_filename} 
            """
    remote_tar = f"/tmp/{temp_filename}"
    remote_script = f"""
            aws s3 cp s3://{bucket}/{prefix}/{temp_filename} {remote_tar}
            mkdir -p {remote}
            tar -xvf {remote_tar} -C {remote}
            """
    docker_mount = f"-v '{abs_remote}':'{abs_docker}'"
    return local_script, remote_script, docker_mount, abs_docker if pypath else None


def output_mount(bucket, prefix, s3_dir, local, remote=None, docker=None, interval=15, pypath=False):
    remote = remote if remote else local
    abs_remote = os.path.abspath(remote)
    assert os.path.isabs(
        docker), "ATTENTION: docker path has to be absolute, to make sure your code knows where it is writing to."
    local_script = f"""
            mkdir -p {local}
            while true; do
                echo "syncing..."
                aws s3 cp s3://{bucket}/{prefix}/{s3_dir} {local} || echo "s3 bucket is EMPTY"
                sleep {interval}
            done & echo "sync {remote} initiated"
    """
    upload = f"""
            aws s3 cp --recursive {remote} s3://{bucket}/{prefix}/{s3_dir} 
            """
    remote_script = f"""
            echo "making log directory {remote}"
            mkdir -p {remote}
            echo "made log directory"
            while true; do
                {upload}
                sleep {interval}
            done & echo "sync {remote} initiated"
            
            while true; do
                if [ -z $(curl -Is http://169.254.169.254/latest/meta-data/spot/termination-time | head -1 | grep 404 | cut -d \  -f 2) ]
                then
                    logger "Running shutdown hook."
                    {upload}
                    break
                else
                    # Spot instance not yet marked for termination. This is hoping that there's at least 3 seconds
                    # between when the spot instance gets marked for termination and when it actually terminates.
                    sleep 3
                fi
            done & echo log sync initiated
            """
    docker_mount = f"-v '{abs_remote}':'{docker}'"
    return local_script, remote_script, docker_mount, upload, docker if pypath else None


def docker_run(docker_image, pypath="", use_gpu=False):
    docker_cmd = "nvidia-docker" if use_gpu else "docker"
    entry_script = "python -m jaynes.entry"
    cmd = f"""echo "Running in docker{' (gpu)' if use_gpu else ''}";""" \
          f"""pip install jaynes""" \
          f"""export PYTHONPATH=$PYTHONPATH{pypath};""" \
          f"""{JAYNES_PARAMS_KEY}={{encoded_thunk}} {entry_script}"""
    docker_container_name = uuid.uuid4()
    test_gpu = f"""
            echo 'Testing nvidia-smi inside docker'
            {docker_cmd} run --rm {docker_image} nvidia-smi
            """
    run_script = f"""
            {test_gpu if use_gpu else "" }
            
            echo 'Now run docker'
            {docker_cmd} run {{docker_mount}} --name {docker_container_name} \\
            {docker_image} /bin/bash -c '{cmd}'
            """
    return run_script
