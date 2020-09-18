## Usage

This CDK application is responsible for creating infrastructure needed by the Amplify for Android integration tests (i.e. `./gradlew cAT` in the `amplify-android` repo). It uses the Amplify CLI to bootstrap and configure an AWS with all the resources needed to support 

Start from the CDK root, where this `README.md` lives:
```console
cd ~/amplify-ci-support/src/integ_test_resources/android/amplify-android/integration/cdk
```

Ensure that you have the CDK installed, if you haven't yet.
```console
npm install -g aws-cdk
```

Ensure that you have [credentials in your environment sufficient to run
the CDK](https://docs.aws.amazon.com/cdk/latest/guide/getting_started.html#getting_started_credentials).

Install CDK dependencies from the root directory of the repo:
```console
# Best to do this in a virtualenv
pip3 install -r requirements.txt
```

**Export credentials and region:**

Export appropriate role credentials to your local shell. Specifically, you must the following environment variables set:
1. `AWS_ACCESS_KEY_ID`
2. `AWS_SECRET_ACCESS_KEY`
3. `AWS_SESSION_TOKEN`

Also, you must set the AWS region to us-east-1:

```console
export AWS_DEFAULT_REGION=us-east-1
```

**Bootstrap the CDK**
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
```

### Deploying a specific stack
**Generate stack template at**
`./cdk.out/<stack_name>.template.json`:

```console
cdk deploy -c region=us-east-1 -c account=******* -c github_owner=<owner> -c branch=<branch_name> -c github_repo=amplify-ci-support
```

**Use that template file to deploy a stack into your AWS account:**
```console
cdk deploy '<stack_name>'
```

**Afterwards, to destroy the stack:**

```console
cdk destroy '<stack_name>'
```
