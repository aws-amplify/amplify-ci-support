
# Release artifacts CDK

Package contains the cdk logic required to create resources that help in integration test in amplify-ios

## Prerequisite

1. AWS CDK - https://docs.aws.amazon.com/cdk/latest/guide/getting_started.html
2. Python3

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

Move to the amplify-ios cdk folder 

```
$ cd src/integ_test_resources/ios/amplify-ios/integration/cdk
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

### 

## Lint

```
$ export SRC_ROOT=/path/to/your/workspace/amplify-ci-support
$ export DIR=$SRC_ROOTsrc/integ_test_resources/ios/amplify-ios/integration/cdk
$ black --line-length=100 $DIR
$ isort -sp $SRC_ROOT/.isort.cfg $DIR
$ flake8 --config $SRC_ROOT/.flake8 $DIR
```