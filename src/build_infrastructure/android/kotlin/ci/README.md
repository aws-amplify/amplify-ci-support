# Amplify Android CI/CD CDK

This project contains the build infrastructure definitions for Amplify Android's CI/CD processes.

## Developing

### Update CDK

To use a new version of the CDK, set the version number in `gradle/libs.versions.toml` and sync the project.

## How to Deploy

### Install dependencies

To deploy the stacks defined in this project you will need to have the [CDK CLI](https://docs.aws.amazon.com/cdk/v2/guide/cli.html) installed.

```
npm install -g aws-cdk
```

### Bootstrap the CDK

This only needs to be done once *per account*. [Bootstrap the account](https://docs.aws.amazon.com/cdk/v2/guide/bootstrapping-env.html) for CDK access by running this command in the terminal:

```
cdk bootstrap --profile <your_aws_cli_profile>
```

### Setup Prerequisites

#### GitHub PAT

A PAT is required to be available in SecretsManager so that CodeBuild can create a webhook for running PR checks.

1. In GitHub, with the `awsmobilesdk` account (or relevant account for the repository being targeted), create a PAT (Classic) with the following scopes:
- repo
- workflow
- admin:repo_hook
2. In the AWS account, create a secret in SecretsManager with the name `github/pat/amplify-android`. Store the PAT under the key `amplify_android_pat`.

### Deploy stacks

To deploy, run the follow command in the terminal:

```
cdk deploy --profile <your_aws_cli_profile>
```