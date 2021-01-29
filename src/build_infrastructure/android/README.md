# Build infrastructure for amplify-android

This CDK app is contains the stacks that manage the AWS components responsible for building and testing pull requests submitted against the main branch of amplify-android.

## Stacks

**Bootstrap stack:** 

Creates some core components in the target account.

**AndroidBuildPipeline stack:** 

This stack sets up the following components:

- **Unit test runner:** CodeBuild project that runs `/gradlew build` and reports the result as a PR check.
- **Integration test runner:** CodeBuild project that run `/graldlew assembleAndroidTest` to create the instrumentation test APKs, which are then executed in DeviceFarm by running `./gradlew runTestsInDeviceFarm`.


## Usage

Ensure that you have the CDK installed, if you haven't yet.
```console
npm install -g aws-cdk
```

Install CDK dependencies from the root directory of the repo:
```console
## Best to do this in a virtualenv
pip3 install -r requirements.txt
```

Start from the CDK app's root, where this `README.md` lives:
```console
cd ~/amplify-ci-support/src/build_infrastructure/android
```

Ensure that you have [credentials in your environment sufficient to run
the CDK](https://docs.aws.amazon.com/cdk/latest/guide/getting_started.html#getting_started_credentials).


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

Bootstrap the CDK (if necessary):
```console
cdk bootstrap
```

### Deploying the stacks
**Generate a single stack template at**
`./cdk.out/<stack_Name>.template.json`:

```bash
cdk deploy AndroidBuildPipeline \
    -c region=us-east-1 \ 
    -c account=<account_id>  \ # AWS Account ID where the stacks will be deployed
    -c github_owner="aws-amplify" \ # Or different owner if testing from a fork.
    -c branch="main" \ # PRs against this branch will trigger the build
    --yes
```

**NOTE 1:** be sure to copy the config files in the bucket whose name contains "amplify-ci-assets" created by the AccountBootstrap.
**NOTE 2:** When deploying in an account for testing purposes, it's a good idea to set the branch to something other than main so the webhook doesn't trigger a build (unless you're modifying/testing the webhook of course).

If necessary, during testing/debugging, add:

```bash
     -c log_level=DEBUG \
```
