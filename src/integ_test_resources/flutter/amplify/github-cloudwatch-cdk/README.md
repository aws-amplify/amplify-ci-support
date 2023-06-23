# Github Cloudwatch CDK For Amplify Flutter Canaries

Relies on cloudformation template 'oidc_provider_stack' for communication between Github and AWS.

Purpose: Provisions Cloudwatch metrics/alarms triggered by amplify-flutter/amplify_canaries GithubAction.

## Usage

1. Follow the 'README.md' of '../oidc_provider_stack' to ensure Github can communicate with your AWS account.
2. Deploy this cdk using the `cdk deploy` cmd line tool.  You can follow the setup instructions for deploying with cdk here: https://docs.aws.amazon.com/cdk/v2/guide/hello_world.html
