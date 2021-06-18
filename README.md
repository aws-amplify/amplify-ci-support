# E2E AWS Token Rotation

This repository contains a cdk stack that spins up a lambda that rotates AWS credentials for use by CircleCI.

## Configuration

The `config.json` file serves three purposes:

1.  Configuration of the CircleCI key's AWS secret
2.  Configuration of the CircleCI project environment (eg. context, project name, slug)
3.  Configuration of who to notify in the case of alarms (triggered when lamdba runs fail)

Start configuring by copy/pasting `cp config.sample.json config.json`, then make the edits as follows:

### 1. Configure your CircleCI api key

This lambda requires access to your CircleCI API Key via AWS Secrets Manager.

Since CDK does not support creating / populating secrets, the secret should be created via the CLI:

```shell
aws secretsmanager create-secret --name circleci-key-secret --secret-string "{ \"amplify_cli_circleci_token\": \"ABC123\" }"
```

Save the `ARN` returned from above operation and paste it into your project's `config.json` file:

```json
"circleCiToken": {
  "arn": "arn:aws:secretsmanager:us-east-2:111111111:secret:amplify_cli_circleci_token-cawIBB",
  "secretKey": "circleci-key-secret"
}
```

### 2. Configure CircleCI project environment

You must update your configuration to point to your CircleCI project, by replacing the sample values with your own CircleCI information:

```json
"cirlceCiConfig": {
  "type": "Context",
  "contextName": "some-context",
  "slug": "gh/someuser",
  "secretKeyIdVariableName": "AWS_ACCESS_KEY_ID",
  "secretKeyVariableName": "AWS_SECRET_ACCESS_KEY",
}
```

### 3. Configure alarm notifications

Finally, include a list of email addresses to be notified when the lambda reaches an alarm state:

```json
{
  "alarmSubscriptions": ["user@domain.com"]
}
```

## Architecture

![architecture diagram](./docs/e2e-token-rotation.svg)

The CDK stack creates all the necessary IAM resources to enable creation of short-lived e2e access tokens. It creates a lambda which hourly publishes those temporary keys as CircleCI environment variables.

## Useful commands

- `npm run build` compile typescript to js
- `npm run watch` watch for changes and compile
- `npm run test` perform the jest unit tests
- `cdk deploy` deploy this stack to your default AWS account/region
- `cdk diff` compare deployed stack with current state
- `cdk synth` emits the synthesized CloudFormation template
