

This CDK application is responsible for creating infrastructure needed by the Amplify for Android integration tests (i.e. `./gradlew :cAT` in the `amplify-android` repo). It uses the Amplify CLI to bootstrap and configure an AWS account with all the resources needed to support that test suite.

Artifacts in this folder and its children fall under one of two categories:
- CDK app assets
- CodeBuild assets

The CDK app, once deployed, creates a CodeBuild project (and associated supporting resources such as roles, policies, etc.) that uses the Amplify CLI to provision backend resources for the integration tests.

## Folder and file structure
When referring to root folder in this document, we're referring to the folder where this `README.md` is located (`<amplify-ci-support root>/src/integ_test_resources/android/amplify/integration/cdk`)

```bash
|
+-- app.py # CDK App
+-- cdk.context.json # CDK App
+-- cdk.json # CDK App
+-- setup.py # CDK App
+-- [stacks] # CDK App
+-- [scripts] # CodeBuild assets
```


## Usage
Start from the CDK root, where this `README.md` lives:
```console
cd <amplify-ci-support root>/src/integ_test_resources/android/amplify/integration/cdk
```

Ensure that you have the CDK installed, if you haven't yet.
```console
npm install -g aws-cdk
```

Ensure that you have [credentials in your environment sufficient to run
the CDK](https://docs.aws.amazon.com/cdk/latest/guide/getting_started.html#getting_started_credentials).

Install CDK dependencies from the root directory of the repo:
```bash
# Best to do this in a virtualenv
pip3 install -r requirements.txt
```

**Export credentials and region:**

Export appropriate role credentials to your local shell. Specifically, you must the following environment variables set:
1. `AWS_ACCESS_KEY_ID`
2. `AWS_SECRET_ACCESS_KEY`
3. `AWS_SESSION_TOKEN`

Also, you must set the AWS region to us-east-1:

```bash
export AWS_DEFAULT_REGION=us-east-1
```

**CDK Context**

The following context variables are used by this application: 

- **region**: typically us-east-1
- **account**: AWS account number
- **github_owner**: defaults to `aws-amplify`, but for testing it's handing to use forks sometimes.
- **branch**:  defaults to `main`

Most cdk commands will require at least region and account. Others are optional.

```bash
# [] denotes optional
-c region=us-east-1 -c account=******* [-c github_owner=<owner>] [-c branch=<branch_name>]
```

**Bootstrap the CDK**

__NOTE__: All CDK commands assume the context parameters are provided.

If you have not yet, bootstrap the CDK:
```console
cdk bootstrap
```

### Deploy all stacks

Note that these steps do each take a _while_.
```console
list=$(cdk list 2>/dev/null | xargs)
cdk synth $list
cdk boostrap $list
cdk deploy $list
```

### Deploying a specific stack
**Generate stack template at**
`./cdk.out/<stack_name>.template.json`:
```console
cdk synth <stack_name> 
```

**Use that template file to deploy a stack into your AWS account:**
```console
cdk deploy '<stack_name>'
```

**Afterwards, to destroy the stack:**

```console
cdk destroy '<stack_name>'
```
