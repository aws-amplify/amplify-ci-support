
# NPM user credentials rotation infrastructure

This CDK app helps to automate the credentials rotation for a NPM user. 
The credentials that are configured for rotation include login password and access keys.

#### Configuring the app
The `lambda_functions/secrets.json` configuration file should be populated with the 
information about the secrets in secrets manager that hold the necessary secrets.

```
{
  "npm_login_username_secret": {
    "arn": "<npm_login_username_secret_arn>",
    "secret_key": "username"
  },
  "npm_login_password_secret": {
    "arn": "<npm_login_password_secret_arn>",
    "secret_key": "password"
  },
  "npm_otp_seed_secret": {
    "arn": "<npm_otp_seed_secret_arn>",
    "secret_key": "npm_otp_seed"
  },
  "npm_access_token_secrets": [
    {
      "arn": "<npm_access_token_codegen_arn>",
      "secret_key": "npm_access_token_codegen"
    },
    {
      "arn": "<npm_access_token_js_arn>",
      "secret_key": "npm_access_token_js"
    }
  ]
}
```
Since, CDK does not support creating/populating the secrets, recommended best practise is
to use the AWS CLI or Console to create the above secrets. 
For example, to create a secret to hold the npm username using CLI:
```
aws secretsmanager create-secret --name npm-username-secret --secret-string "{ \"username\": \"my-npm-username\" }"
```
Paste the `ARN` returned from above operation under `npm_login_username_secret`.
The `secret_key` (`username` in this case) can also be customized.

Similarly, create the other secrets required in the configuration file:
* `npm_login_username_secret`: stores the login username for the npm user. This secret is static and is not rotated.
* `npm_login_password_secret`: stores the login password for the npm user. This secret is configured for rotation.
* `npm_otp_seed_secret`: stores the OTP seed for the npm user. This is created when the NPM user enables 2-factor Authentication. 
This secret is static and is not rotated.
* `npm_access_token_secrets`: stores the list of secrets that hold the access keys created by the npm user. 
This secret is configured for rotation.

#### Deploying the infrastructure
The AWS credentials have to be set using following environment variables:
  1. `AWS_ACCESS_KEY_ID`
  2. `AWS_SECRET_ACCESS_KEY`
  3. `AWS_SESSION_TOKEN`
  4. `AWS_DEFAULT_REGION`: The region of deployment should be same as the region where the above secrets are created.

`python 3` and `pip3` should be installed.
Run `pip3 install -r requirements.txt --upgrade` from the app root to fetch necessary modules for the app.

At this point you can now deploy the infrastructure using:
```
$ cdk deploy
```
or run any of the cdk commands listed below.


#### Useful commands

 * `cdk ls`          list all stacks in the app
 * `cdk synth`       emits the synthesized CloudFormation template
 * `cdk deploy`      deploy this stack to your default AWS account/region
 * `cdk diff`        compare deployed stack with current state
 * `cdk docs`        open CDK documentation


#### Stacks included in the app
* `UserLoginPasswordRotatorStack`: Contains resources like a rotator lambda to rotate the `npm_login_password_secret` 
along with necessary permissions, alarms to monitor it.
* `UserAccessTokensRotatorStack`: Contains resources like a rotator lambda to rotate the access keys specified under `npm_access_token_secrets` 
along with necessary permissions, alarms to monitor it.

To deploy a single stack, use `cdk deploy UserLoginPasswordRotatorStack`

------------------

[amplify.aws](https://amplify.aws)

