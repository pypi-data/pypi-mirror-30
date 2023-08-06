import os

from jaynes.components import s3_mount, output_mount, docker_run
from jaynes.param_codec import serialize
from jaynes.shell import ck


class Jaynes:
    def __init__(self, bucket, prefix="jaynes", log=None):
        self.bucket = bucket
        self.prefix = prefix
        self.log = log if log else "/tmp/jaynes/startup.log"
        self.pypath = ""
        self.local_setup = ""
        self.upload_script = ""
        self.remote_setup = ""
        self.docker_mount = ""

    config = __init__

    def mount_s3(self, **kwargs):
        local_script, remote_script, docker_mount, _pypath = s3_mount(self.bucket, self.prefix, **kwargs)
        if _pypath:
            self.pypath += ":" + _pypath
        self.local_setup += local_script
        self.remote_setup += remote_script
        self.docker_mount += " " + docker_mount
        return self

    def mount_output(self, **kwargs):
        """
        > `s3_dir` is prefixed with bucket name and prefix.
        """
        local_script, remote_script, docker_mount, upload, _pypath = output_mount(self.bucket, self.prefix, **kwargs)
        if _pypath:
            self.pypath += ":" + _pypath
        self.local_setup += local_script
        self.upload_script += upload
        self.remote_setup += remote_script
        self.docker_mount += " " + docker_mount
        return self

    def setup_docker_run(self, docker_image, use_gpu=False):
        self.docker_image = docker_image
        self.use_gpu = use_gpu
        return self

    def run_local(self, dry=False):
        if dry:
            return self.local_setup
        else:
            ck(self.local_setup, shell=True)
            return self

    def run_docker(self, fn, *args, dry=False, **kwargs):
        main_log = self.log
        log_dir = os.path.dirname(main_log)
        encoded_thunk = serialize(fn, args, kwargs)
        docker_command = docker_run(self.docker_image, self.pypath, self.use_gpu) \
            .format(encoded_thunk=encoded_thunk, docker_mount=self.docker_mount)
        remote_script = f"""
        #!/bin/bash
        mkdir -p {log_dir}
        {{
            # clear log
            truncate -s 0 {main_log}
            
            {self.remote_setup}
            
            # sudo service docker start
            # pull docker
            docker pull {self.docker_image}
            
            {docker_command}
            
            {self.upload_script}
        }} >> {main_log}
        """
        if dry:
            return remote_script
        else:
            ck(remote_script, shell=True)
            return self

    def run_remote(self, dry=False):
        tag_current_instance = """
            EC2_INSTANCE_ID="`wget -q -O - http://169.254.169.254/latest/meta-data/instance-id`"
            aws ec2 create-tags --resources $EC2_INSTANCE_ID --tags Key=Name,Value=infogan-rope-2018-03-28-10-18-16-000 --region us-west-2
            aws ec2 create-tags --resources $EC2_INSTANCE_ID --tags Key=exp_prefix,Value=infogan-rope --region us-west-2
        """
        install_aws_cli = """
            curl "https://s3.amazonaws.com/aws-cli/awscli-bundle.zip" -o "awscli-bundle.zip"
            yes A | unzip awscli-bundle.zip
            sudo ./awscli-bundle/install -i /usr/local/aws -b /usr/local/bin/aws
            echo "aws cli is installed"
        """
        test_script = """
            echo 'Testing nvidia-smi'
            nvidia-smi
        """
        termination_script = f"""
            echo "Now terminate this instance"
            EC2_INSTANCE_ID="`wget -q -O - http://169.254.169.254/latest/meta-data/instance-id || die "wget instance-id has failed: $?"`"
            # aws ec2 terminate-instances --instance-ids $EC2_INSTANCE_ID --region us-west-2
        """
        main_log = "/home/ubuntu/user_data.log"
        log_dir = os.path.dirname(main_log)
        log_wrapper = f"""
        #!/bin/bash
        mkdir -p {log_dir}
        {{
            # clear log
            truncate -s 0 {main_log}
            
            die() {{ status=$1; shift; echo "FATAL: $*"; exit $status; }}
            {install_aws_cli}
            
            export AWS_DEFAULT_REGION=us-west-1
            {tag_current_instance}
            
            {self.remote_setup}
            
            # sudo service docker start
            # pull docker
            docker --config /home/ubuntu/.docker pull thanard/matplotlib:latest
            
            {test_script}
            
            {test_docker}
            
            {self.run_script}
            
            {termination_script}
        }} >> {main_log}
        """
        if dry:
            return log_wrapper
        else:
            ck(self.local_setup, shell=True)
            return self
