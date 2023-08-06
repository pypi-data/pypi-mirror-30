Jaynes, A Utility for training ML models on AWS with docker
===========================================================

Todo
----

-  [x] get the initial template to work

Done
~~~~

Installation
------------

.. code-block:: bash

    pip install jaynes

Usage (**Show me the Mo-NAY!! :moneybag::money\_with\_wings:**)
---------------------------------------------------------------

Take a look at the folder `test\_projects/ <test_projects/>`__! These
project scripts are used for test and development, so they should work
out-of-the-box (if you have the right box ahem).

To run Local Docker
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from jaynes import Jaynes, templates
    from main import train, RUN

    S3_PREFIX = "s3://ge-bair/code-block/new-experiment/"
    J = Jaynes(
        launch_log="jaynes_launch.log",
        mounts=[
            templates.S3Mount(local="https://github.com/episodeyang/jaynes/blob/master/", s3_prefix=S3_PREFIX, pypath=True),
            templates.S3Mount(local=".https://github.com/episodeyang/jaynes/blob/master/.https://github.com/episodeyang/jaynes/blob/master/", s3_prefix=S3_PREFIX, pypath=True, file_mask="https://github.com/episodeyang/jaynes/blob/master/__init__.py https://github.com/episodeyang/jaynes/blob/master/jaynes"),
            templates.S3UploadMount(docker_abs=RUN.log_dir, s3_prefix=S3_PREFIX, local=RUN.log_dir, sync_s3=True)
        ],
    )
    J.set_docker(
        docker=templates.DockerRun("python:3.6",
                                   pypath=":".join([m.pypath for m in J.mounts if hasattr(m, "pypath") and m.pypath]),
                                   docker_startup_scripts=("pip install cloudpickle",),
                                   docker_mount=" ".join([m.docker_mount for m in J.mounts]),
                                   use_gpu=False).run(train, log_dir=RUN.log_dir)
    )
    J.run_local_setup(verbose=True)
    J.launch_local_docker(verbose=True, delay=30)

To run on remote server with ssh
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from jaynes import Jaynes, templates
    from main import train, RUN

    S3_PREFIX = "s3://ge-bair/code-block/run_remote/"

    output_mount = templates.S3UploadMount(docker_abs=RUN.log_dir, s3_prefix=S3_PREFIX, local=RUN.log_dir, sync_s3=True)

    J = Jaynes(
        launch_log="jaynes_launch.log",
        mounts=[
            templates.S3Mount(local="https://github.com/episodeyang/jaynes/blob/master/", s3_prefix=S3_PREFIX, pypath=True),
            templates.S3Mount(local=".https://github.com/episodeyang/jaynes/blob/master/.https://github.com/episodeyang/jaynes/blob/master/", s3_prefix=S3_PREFIX, pypath=True, file_mask="https://github.com/episodeyang/jaynes/blob/master/__init__.py https://github.com/episodeyang/jaynes/blob/master/jaynes"),
            output_mount
        ],
    )
    J.set_docker(
        docker=templates.DockerRun("python:3.6",
                                   pypath=":".join([m.pypath for m in J.mounts if hasattr(m, "pypath") and m.pypath]),
                                   docker_startup_scripts=("pip install cloudpickle",),
                                   docker_mount=" ".join([m.docker_mount for m in J.mounts]),
                                   use_gpu=False).run(train, log_dir=RUN.log_dir)
    )
    J.run_local_setup(verbose=True)
    J.make_launch_script(log_dir=output_mount.remote_abs, instance_tag=RUN.instance_prefix, sudo=True,
                         terminate_after_finish=True)
    J.launch_ssh(ip_address="52.11.206.135", pem="~/.ec2/ge-berkeley.pem", script_dir=output_mount.remote_abs, verbose=True)

To Launch EC2 instance and Run on Startup
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

make sure the instance terminate after docker run!

.. code-block:: python

    from jaynes import Jaynes, templates
    from main import train, RUN

    S3_PREFIX = "s3://ge-bair/code-block/run_ssh/"

    output_mount = templates.S3UploadMount(docker_abs=RUN.log_dir, s3_prefix=S3_PREFIX, local=RUN.log_dir, sync_s3=True)

    J = Jaynes(
        launch_log="jaynes_launch.log",
        mounts=[
            templates.S3Mount(local="https://github.com/episodeyang/jaynes/blob/master/", s3_prefix=S3_PREFIX, pypath=True),
            templates.S3Mount(local=".https://github.com/episodeyang/jaynes/blob/master/.https://github.com/episodeyang/jaynes/blob/master/", s3_prefix=S3_PREFIX, pypath=True, file_mask="https://github.com/episodeyang/jaynes/blob/master/__init__.py https://github.com/episodeyang/jaynes/blob/master/jaynes"),
            output_mount
        ],
    )
    J.set_docker(
        docker=templates.DockerRun("python:3.6",
                                   pypath=":".join([m.pypath for m in J.mounts if hasattr(m, "pypath") and m.pypath]),
                                   docker_startup_scripts=("pip install cloudpickle",),
                                   docker_mount=" ".join([m.docker_mount for m in J.mounts]),
                                   use_gpu=False).run(train, log_dir=RUN.log_dir)
    )
    J.run_local_setup(verbose=True)
    J.make_launch_script(log_dir=output_mount.remote_abs, instance_tag=RUN.instance_prefix, sudo=False,
                         terminate_after_finish=True)
    J.launch_ec2(region="us-west-2", image_id="ami-bd4fd7c5", instance_type="p2.xlarge", key_name="ge-berkeley",
                 security_group="torch-gym-prebuilt", spot_price=None,
                 iam_instance_profile_arn="arn:aws:iam::055406702465:instance-profile/main", dry=False)

Jaynes does the following:

1. 

To Develop
----------

.. code-block:: bash

    git clone https://github.com/episodeyang/jaynes.git
    cd jaynes
    make dev

To test, run

.. code-block:: bash

    make test

This ``make dev`` command should build the wheel and install it in your
current python environment. Take a look at the
`https://github.com/episodeyang/jaynes/blob/master/Makefile <https://github.com/episodeyang/jaynes/blob/master/Makefile>`__ for details.

**To publish**, first update the version number, then do:

.. code-block:: bash

    make publish

Acknowledgements
----------------

This code-block is inspired by @justinfu's
`doodad <https://github.com/justinjfu/doodad>`__, which is in turn built
on top of Peter Chen's script.

This code-block is written from scratch to allow a more permissible
open-source license (BSD). Go bears :bear: !!


