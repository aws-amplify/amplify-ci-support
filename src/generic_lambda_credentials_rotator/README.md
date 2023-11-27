# Generic Lambda Credentials Rotator

Generic Lambda Credentials Rotator is a AWS Lambda function that can be used to move credentials and other artifacts from one source to another destination. This package can be included into any cdk package to enable credential rotation. Few use cases:

1. Create temprorary AWS credentials and push the credentials to CircleCI environment variable. 
2. Move values in lambda environment variable to CircleCI environment variable. 
3. Move values in AWS Secrets Manager to CircleCI environment variable.

## Destination supported:

- CircleCI environment variable
    - Input structure:
    ```
    "<destination_name>": {
          "type": "cci_env_variable",
          "description": "<Description of what this destination is>",
          "github_path": "<github_user>/<github_repo>",
          "circleci_api_token_secret_id_lambda_env_var_key": "<Lambda environment variable key that has the key to the AWS Secrets Manager>"
        }
    ```
    - AWS Lambda requires api token from CircleCI to push values to CircleCI environment variable. This api key should be stored in AWS Secrets Manager, and the key for the secret should be stored as environment variable in lambda function. `circleci_api_token_secret_id_lambda_env_var_key` above stores the key info for this lambda environment variable. 

## Sources supported:

- AWS Session Credentials
- Lambda environment Variables
- Secrets in AWS Secrets Manager

## Complete Input format:

```cli
{
      "sources": [
        {
          "type": "aws_session_cred",
          "description": "Temporary AWS Credentials to upload the release artifacts to S3 and invalidate Cloudfront",
          "configuration": {
            "user_env_variable": "IAM_USERNAME",
            "iam_role_env_variable": "IAM_ROLE"
          },
          "destination": {
            "specifier": "aws-sdk-ios-cci",
            "mapping_to_destination": [
              {
                "destination_key_name": "XCF_ACCESS_KEY_ID",
                "result_value_key": "access_key_id"
              },
              {
                "destination_key_name": "XCF_SECRET_ACCESS_KEY",
                "result_value_key": "secret_access_key"
              },
              {
                "destination_key_name": "XCF_SESSION_TOKEN",
                "result_value_key": "session_token"
              }
            ]
          }
        },
        {
          "type": "secrets_manager",
          "description": "",
          "configuration": {
            "secret_key_env_variable": "GITHUB_CREDENTIALS_SECRET"
          },
          "destination": {
            "specifier": "aws-sdk-ios-cci",
            "mapping_to_destination": [
              {
                "destination_key_name": "GITHUB_SPM_TOKEN",
                "result_value_key": "GITHUB_SPM_TOKEN"
              },
              {
                "destination_key_name": "GITHUB_SPM_USER",
                "result_value_key": "GITHUB_SPM_USER"
              }
            ]
          }
        },
        {
          "type": "lambda_env_variables",
          "description": "",
          "configuration": {
            "lambda_env_var_key": "SPM_S3_BUCKET_NAME"
          },
          "destination": {
            "specifier": "aws-sdk-ios-cci",
            "mapping_to_destination": [
              {
                "destination_key_name": "XCF_S3_BUCKET_NAME"
              }
            ]
          }
        }
      ],
      "destinations": {
        "aws-sdk-ios-cci": {
          "type": "cci_env_variable",
          "description": "Circle CI environment variable for AWS SDK iOS repo",
          "github_path": "aws-amplify/aws-sdk-ios",
          "circleci_api_token_secret_id_lambda_env_var_key": "CIRCLE_CI_IOS_SDK_API_TOKEN"
        }
      }
    }

```