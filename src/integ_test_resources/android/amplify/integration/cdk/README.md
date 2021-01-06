# Integration test resources for amplify-android

This CDK application is responsible for creating infrastructure needed by [the Amplify for Android integration tests](https://github.com/aws-amplify/amplify-android/blob/main/CONTRIBUTING.md#run-instrumentation-tests). It uses the Amplify CLI to bootstrap and configure an AWS account with all the resources needed to support that test suite.

Artifacts in this folder and its children fall under one of two categories:
- CDK app assets
- CodeBuild assets

The CDK app, once deployed, creates a CodeBuild project (and associated supporting resources such as roles, policies, etc.) that uses the Amplify CLI to provision backend resources for the integration tests.

## Folder and file structure
When referring to "root" folder in this document, we're referring to the folder where this `README.md` is located (`<amplify-ci-support root>/src/integ_test_resources/android/amplify/integration/cdk`)

```bash
|
+-- app.py # CDK App
+-- cdk.context.json # CDK App
+-- cdk.json # CDK App
+-- setup.py # CDK App
+-- [stacks] # CDK App
+-- [scripts] # CodeBuild assets
```

## Pre-requisites

1. Go to the root folder of the `amplify-ci-support` repository.
```console
cd <amplify-ci-support root>
```

2. Ensure that you have the CDK installed, if you haven't yet.
```console
npm install -g aws-cdk
```

3. Setup a Python virtualenv (Python 3.8) and activate it.

4. Install CDK dependencies from the root directory of the repo:
```bash
pip3 install -r requirements.txt
```

5. Setup AWS credentials for your local shell.

Export appropriate role credentials to your local shell. Specifically, you must the following environment variables set:
1. `AWS_ACCESS_KEY_ID`
2. `AWS_SECRET_ACCESS_KEY`
3. `AWS_SESSION_TOKEN`

Also, you must set the AWS region to us-east-1:

```bash
export AWS_DEFAULT_REGION=us-east-1
```

## Usage
There are two parts to this CDK application: 
- The CDK app itself which deploys a Cloudformation stack with a CodeBuild project.
- The scripts that are executed inside the CodeBuild project.

That being said, there are a couple of different usage scenarios:
1. You just want to setup the backend resources against your own AWS account for running the tests, adding/modifying test scenarios, etc. In this case, you would be running the scripts that run inside CodeBuild on your local environment.
2. You are setting a new AWS account for integration testing purposes and you want changes made to the `scripts` and/or `schemas`  folders to be executed from the CodeBuild project when something is committed to a branch.

### Option 1 - Run the scripts locally
Ensure your AWS credentials have rights to execute the script.

1. Start from the CDK app root, where this `README.md` lives:
```console
cd <amplify-ci-support root>/src/integ_test_resources/android/amplify/integration/cdk
```

2. Run one of the deployment scripts located under the `scripts` folder. For example:
```Console
python ./scripts/deploy_api_tests_backend.sh
```

### Option 2 - Setup a new AWS account to run integration tests
Ensure that you have [credentials in your environment sufficient to run
the CDK](https://docs.aws.amazon.com/cdk/latest/guide/getting_started.html#getting_started_credentials).

If you want to setup a new AWS account with the backend resources necessary to run integration tests, you will need to setup and deploy the CDK app by following these steps:

Most cdk commands will require at least region and account. Others are optional.

```bash
# [] denotes optional
-c region=us-east-1 -c account=******* [-c github_owner=<owner>] [-c branch=<branch_name>]
```

__NOTE__: All CDK commands assume the context parameters are provided.

**CDK Context**

The following context variables are used by this application: 

- **region**: typically us-east-1
- **account**: AWS account number
- **github_owner**: defaults to `aws-amplify`, but for testing it's handing to use forks sometimes.
- **branch**:  defaults to `main`

1. Start from the CDK app root, where this `README.md` lives:
```console
cd <amplify-ci-support root>/src/integ_test_resources/android/amplify/integration/cdk
```

2. Bootstrap the CDK

If you have not yet, bootstrap the CDK:
```console
cdk bootstrap
```

3. Deploy the application
Currently, there is only one stack in this app, so it's not necessary to pass the `stack_name` parameter. As this application evolves, it may become necessary to provide the stack name as part of the cdk commands.

**Generate stack template at**
`./cdk.out/<stack_name>.template.json`:
```console
cdk synth <context parameters>
```

**Use that template file to deploy a stack into your AWS account:**
```console
cdk deploy <context parameters>
```

**Afterwards, to destroy the stack:**

```console
cdk destroy <context parameters>
```
