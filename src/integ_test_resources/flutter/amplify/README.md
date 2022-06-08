# OIDC Provider Stack For Amplify Flutter Integration Tests

This AWS CloudFormation template was created for use in the [Amplify Flutter](https://github.com/aws-amplify/amplify-flutter) repository but could be used for anyone wishing to use Github Actions with Amplify projects.

This template can be used to provision a stack in an AWS account so that Github Actions can run `amplify pull`. When provisioned from the AWS console, this stack will give a Github repo the ability to use the [OpenID Connect integration with AWS](https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/configuring-openid-connect-in-amazon-web-services) with sufficient permissions to run `amplify pull` and get read-only access to Amplify projects in the account. It is designed to be used with the [Configure AWS Credentials Action](https://github.com/aws-actions/configure-aws-credentials).

## Usage

### Create the stack from the template:

1. Download the cloudformation_template.yaml file to somewhere that is convenient to upload from.
2. Go into the AWS Console for the account you wish to connect. Search for "CloudFormation" in the search bar and click on "CloudFormation" to go to CloudFormation console.
3. Click button "Create stack" > "With new resources (standard)".
4. Select "Upload a template file" and click "Choose file," selecting the template file you downloaded from step 1.
5. Click "Next."
6. Enter a stack name such as "GithubAmplifyOIDC."
7. For "FullRepoName" field, enter identifier for the Github repository such as "aws-amplify/amplify-flutter." Only Github Actions from this repository will be able to use the generated OIDC provider stack because Github will provide this as a parameter when requesting credentials from AWS and the configured stack will check that parameter.
8. Click "Next."
9. Click "Next" again. There is nothing to change on this page.
10. Scroll down to the bottom and click the checkbox next to "I acknowledge that AWS CloudFormation might create IAM resources with custom names."
11. Click "Create stack."

Wait for the stack to finish creating, which should take less than 30 seconds.

### Connect Github Actions to the OIDC provider

1. Get the ARN of the generated "pull_amplify_integration_test_configs" IAM role. You will need to use this in your Github Action to tell Github which role to fetch credentials for. It is recommended to store this as a secret in your Github repository. You can get the ARN by navigating to "Stacks" in the CloudFormation console and searching for the name of the stack you used. Click on the stack, and click on the "Resources" tab. Click on the link next to "Role" which will take you to the role in the IAM console. There, you should see the ARN.
2. Add the ARN value as a secret named "AWS_IAM_ROLE_ARN" to your repo. See [Github docs](https://docs.github.com/en/rest/actions/secrets).
3. Use the [Configure AWS Credentials Action](https://github.com/aws-actions/configure-aws-credentials) and supply the secret as the value to `role-to-assume` as seen on https://github.com/aws-actions/configure-aws-credentials#examples in addition to the region that contains your Amplify backends. At this point, every execution of this Action will have temporary AWS credentials as redacted environmental variables you can use to run `amplify pull`.
4. Run a script to pull the amplify environment. Such as:

```bash
# Amplify needs a profile to run headless pulls because CLI does not support session token.
aws configure set aws_access_key_id $AWS_ACCESS_KEY_ID
aws configure set aws_secret_access_key $AWS_SECRET_ACCESS_KEY
aws configure set aws_session_token $AWS_SESSION_TOKEN
aws configure set default.region $AWS_DEFAULT_REGION

# Amplify headless pull

FLUTTERCONFIG="{\
\"ResDir\":\"./lib/\",\
\"SourceDir\":\"lib\",\
}"

AMPLIFY="{\
\"appId\":\"my-app-id\",\
\"envName\":\"test\",\
\"defaultEditor\":\"code\"\
}"

FRONTEND="{\
\"frontend\":\"flutter\",\
\"config\":$FLUTTERCONFIG\
}"

AWSCLOUDFORMATIONCONFIG="{\
\"configLevel\":\"project\",\
\"useProfile\":true,\
\"profileName\":\"default\",\
\"region\":\"us-east-1\"\
}"
PROVIDERS="{\
\"awscloudformation\":$AWSCLOUDFORMATIONCONFIG\
}"

echo n | amplify pull \
--amplify $AMPLIFY \
--frontend $FRONTEND \
--providers $PROVIDERS
```
