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

Install CDK dependencies:
```console
# Best to do this in a virtualenv
pip install -r requirements.txt
```

Generate a Pinpoint stack template at
`./cdk.out/pinpoint.template.json`:

```console
cdk synth 'pinpoint'
```

Use that template file to deploy a stack into your AWS account:
```console
cdk deploy 'pinpoint'
```

Afterwards, to destroy the stack:

```console
cdk destroy 'pinpoint'
```

