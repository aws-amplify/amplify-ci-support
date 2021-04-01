
# Release artifacts CDK

Package contains the cdk logic required to create release artifacts for Amplify resources.

## Prerequisite

1. AWS CDK - https://docs.aws.amazon.com/cdk/latest/guide/getting_started.html
2. Python3
3. Docker - https://www.docker.com

## Setup

```
$ cd /path to workspace/amplify-ci-support
```

To manually create a virtualenv on MacOS and Linux:

```
$ python3 -m venv .venv
```

After the init process completes and the virtualenv is created, you can use the following
step to activate your virtualenv.

```
$ source .venv/bin/activate
```

If you are a Windows platform, you would activate the virtualenv like this:

```
% .venv\Scripts\activate.bat
```

Once the virtualenv is activated, you can install the required dependencies.

```
$ pip install -r requirements.txt
```

Move to the resources cdk folder 

```
$ cd src/release_artifacts_resources/ios/cdk
```

At this point you can list the stacks available

```
$ cdk ls
```

To add additional dependencies, for example other CDK libraries, just add
them to your `requirements.txt` file and rerun the `pip install -r requirements.txt`
command.

## Useful commands

 * `cdk ls`          list all stacks in the app
 * `cdk synth`       emits the synthesized CloudFormation template
 * `cdk deploy`      deploy this stack to your default AWS account/region
 * `cdk diff`        compare deployed stack with current state
 * `cdk docs`        open CDK documentation

## Stack information

### Distribution stack

Release resources for distribution are declared in the stack named - `DistributionStack`. This include resources like S3 and Cloudfront needed for hosting the release artifacts. This stack should be run only once.

### Credential rotation stack

Resources required for credential rotation are declared in `CredentialRotationStack`. This stack uses `aws_cdk.aws_lambda_python` which requires `Docker` running in your local machine to execute `cdk` commands.


## Lint

```
$ export SRC_ROOT=/path/to/your/workspace/amplify-ci-support
$ export DIR=$SRC_ROOT/src/release_artifacts_resources/ios/cdk
$ black --line-length=100 $DIR
$ isort -sp $SRC_ROOT/.isort.cfg $DIR
$ flake8 --config $SRC_ROOT/.flake8 $DIR
```