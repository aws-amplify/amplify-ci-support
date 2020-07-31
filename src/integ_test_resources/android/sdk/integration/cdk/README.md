## Usage

Each test suite has a separate CDK stack that can be used to set up the
resources required to run that test suite.

Let's take the Pinpoint test suite as an example. To bring up the
resources required (a Pinpoint application and a Cognito identity pool),
follow the steps below.

Start from the CDK root, where this `README.md` lives:
```console
cd ~/amplify-ci-support/src/integ_test_resources/android/sdk/integration/cdk
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
cdk synth 'pinpoint'
```

**Use that template file to deploy a stack into your AWS account:**
```console
cdk deploy 'pinpoint'
```

**Afterwards, to destroy the stack:**

```console
cdk destroy 'pinpoint'
```

## Caveats

The S3 suite requires use of some public buckets. As a result, you need
to *allow* public buckets in your account, at all. (By default, AWS no
long does, for security reasons.) This step only needs to be performed
once, on the test account.

[Instructions to allow S3 public access, here](https://docs.aws.amazon.com/AmazonS3/latest/dev/access-control-block-public-access.html#console-block-public-access-options)
