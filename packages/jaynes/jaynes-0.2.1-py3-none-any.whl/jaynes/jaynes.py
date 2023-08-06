import base64
import os
from textwrap import dedent

from .components import s3_mount, output_mount, docker_run, ssh_remote_exec
from .param_codec import serialize
from .shell import ck


class Jaynes:
    def __init__(self, remote_cwd, bucket, prefix="jaynes", log=None):
        self.bucket = bucket
        self.prefix = prefix
        self.remote_cwd = remote_cwd
        self.main_log = log
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

        s3 path syntax:
                    s3://{bucket}/{prefix}/{s3_dir}
        local path syntax:
                    file://{local}
                note if local is None, no local folder will be created to downloaded.
        remote path syntax:
                    ssh://<remote>:{remote_cwd, remote}
                note that the remote path is made absolute using the remote_cwd parameter
        :param kwargs:
        :return:
        """
        local_script, remote_script, docker_mount, upload, _pypath = \
            output_mount(remote_cwd=self.remote_cwd, bucket=self.bucket, prefix=self.prefix, **kwargs)
        if _pypath:
            self.pypath += ":" + _pypath
        self.local_setup += local_script
        self.upload_script += upload
        self.remote_setup += remote_script
        self.docker_mount += " " + docker_mount
        return self

    def setup_docker_run(self, docker_image, docker_startup_scripts=None, use_gpu=False):
        self.docker_image = docker_image
        self.use_gpu = use_gpu
        self.docker_startup_scripts = docker_startup_scripts
        return self

    def run_local(self, verbose=False, dry=False):
        cmd = f"""{self.local_setup}"""
        if dry:
            return cmd
        else:
            ck(cmd, verbose=verbose, shell=True)
            return self

    def run_local_docker(self, fn, *args, verbose=False, dry=False, **kwargs):
        abs_log = os.path.abspath(self.main_log)
        log_dir = os.path.dirname(abs_log)
        encoded_thunk = serialize(fn, args, kwargs)
        docker_command = docker_run(self.docker_image, self.pypath, self.docker_startup_scripts, os.getcwd(),
                                    self.use_gpu).format(encoded_thunk=encoded_thunk, docker_mount=self.docker_mount)
        remote_script = f"""
        #!/bin/bash
        mkdir -p {log_dir}
        {{
            # clear main_log
            truncate -s 0 {abs_log}
            
            {self.remote_setup}
            
            # sudo service docker start
            # pull docker
            docker pull {self.docker_image}
            {docker_command}
            {self.upload_script}
            
        }} >> {self.abs_log}
        """
        if dry:
            return remote_script
        else:
            ck(remote_script, verbose=verbose, shell=True)
            return self


    def make_launch_script(self, fn, *args, verbose=False, sudo=False, terminate_after_finish=False, **kwargs):
        tag_current_instance = f"""
            EC2_INSTANCE_ID="`wget -q -O - http://169.254.169.254/latest/meta-data/instance-id`"
            aws ec2 create-tags --resources $EC2_INSTANCE_ID --tags Key=Name,Value={self.prefix} --region us-west-2
            aws ec2 create-tags --resources $EC2_INSTANCE_ID --tags Key=exp_prefix,Value={self.prefix} --region us-west-2
        """
        install_aws_cli = f"""
            curl "https://s3.amazonaws.com/aws-cli/awscli-bundle.zip" -o "awscli-bundle.zip"
            yes A | unzip awscli-bundle.zip
            echo "finished unziping the awscli bundle"
            {"sudo " if sudo else ""}./awscli-bundle/install -i /usr/local/aws -b /usr/local/bin/aws
            echo "aws cli is installed"
        """
        termination_script = f"""
            echo "Now terminate this instance"
            EC2_INSTANCE_ID="`wget -q -O - http://169.254.169.254/latest/meta-data/instance-id || die "wget instance-id has failed: $?"`"
            aws ec2 terminate-instances --instance-ids $EC2_INSTANCE_ID --region us-west-2
        """
        # TODO: path.join is running on local computer, so it might not be quite right if remote is say windows.
        abs_log = os.path.join(self.remote_cwd, self.main_log)
        log_dir = os.path.dirname(abs_log)
        encoded_thunk = serialize(fn, args, kwargs)
        docker_command = docker_run(self.docker_image, self.pypath, self.docker_startup_scripts, os.getcwd(),
                                    self.use_gpu).format(encoded_thunk=encoded_thunk, docker_mount=self.docker_mount)
        launch_script_path = os.path.join(os.path.dirname(self.main_log), "jaynes_launcher.sh")
        launch_script = f"""
        #!/bin/bash
        mkdir -p {log_dir}
        {{
            # clear main_log
            truncate -s 0 {abs_log}
            
            die() {{ status=$1; shift; echo "FATAL: $*"; exit $status; }}
            {install_aws_cli}
            
            export AWS_DEFAULT_REGION=us-west-1
            {tag_current_instance}
            
            {self.remote_setup}
            
            # {"sudo " if sudo else ""}service docker start
            # pull docker
            docker pull {self.docker_image}
            
            {self.upload_script}
            {docker_command}
            {termination_script if terminate_after_finish else ""}
        }} >> {abs_log}
        """

        launch_script = dedent(launch_script).strip()
        with open(launch_script_path, 'w+') as f:
            f.write(launch_script)

        self.launch_script = launch_script
        self.launch_script_path = launch_script_path
        if verbose:
            print(self.launch_script)
        return self

    def run_ssh_remote(self, ip_address, pem=None, verbose=False, dry=False):
        """
        run launch_script remotely by ip_address
        :param ip_address:
        :param pem:
        :param verbose:
        :param dry:
        :return:
        """
        cmd = ssh_remote_exec("ubuntu", ip_address, pem=pem, script=self.launch_script_path)
        if dry:
            print(cmd)
        else:
            ck(cmd, verbose=verbose, shell=True)


    def launch_and_run(self, region, image_id, instance_type, key_name, security_group,
                       spot_price=None, iam_instance_profile_arn=None, verbose=False,
                       dry=False):
        import boto3
        ec2 = boto3.client("ec2", region_name=region, aws_access_key_id=os.environ.get('AWS_ACCESS_KEY'),
                           aws_secret_access_key=os.environ.get('AWS_ACCESS_SECRET'))

        instance_config = dict(ImageId=image_id, KeyName=key_name, InstanceType=instance_type,
                               SecurityGroups=(security_group,),
                               IamInstanceProfile=dict(Arn=iam_instance_profile_arn),
                               UserData=base64.b64encode(self.launch_script.encode()).decode("utf-8"))
        if spot_price:
            # for detailed settings see: http://boto3.readthedocs.io/en/latest/reference/services/ec2.html#EC2.Client.request_spot_instances
            response = ec2.request_spot_instances(InstanceCount=1, LaunchSpecification=instance_config,
                                                  SpotPrice=str(spot_price), DryRun=dry)
            spot_request_id = response['SpotInstanceRequests'][0]['SpotInstanceRequestId']
            print(response)
            return spot_request_id
        else:
            response = ec2.run_instances(MaxCount=1, MinCount=1, **instance_config, DryRun=dry)
            print(response)
            return response
