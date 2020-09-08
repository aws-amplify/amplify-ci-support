## Usage

Start from the CDK root, where this `README.md` lives:
```console
cd ~/amplify-ci-support/src/build_infrastructure_resources/android
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
**Generate a Pinpoint stack template at**
`./cdk.out/pinpoint.template.json`:

```console
cdk synth 'AndroidBuildPipelineStack' -c region=us-east-1 -c account=<target_account>
```

**Use that template file to deploy a stack into your AWS account:**
```console
cdk deploy 'AndroidBuildPipelineStack' -c region=us-east-1 -c account=<target_account>
```

**Afterwards, to destroy the stack:**

```console
cdk destroy 'build_pipeline_stack' -c region=us-east-1 -c account=<target_account>
```

## Caveats