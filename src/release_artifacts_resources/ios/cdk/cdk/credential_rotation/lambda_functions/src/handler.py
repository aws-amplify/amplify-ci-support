import json
from models.source_type import SourceType
from models.destination_type import DestinationType
from source_data_generator import aws_session_credential_source
from destination import circleci

def handler(event, context, *, iam=None, sts=None, secretsmanager=None):
    """
    Invoked with the following event structure:
    ```
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
          "circleci_api_token_secret_arn_lambda_env_var_key": "CIRCLE_CI_IOS_SDK_API_TOKEN"
        }
      }
    }
    ```
    """

    event_object = json.loads(event)
    sources = event_object["sources"]
    destinations = event_object["destinations"]

    destination_values_map = {}
    for source in sources:
        source_type = source["type"]
        destination_specifier = source["destination"]["specifier"]
        destination_mapping = source["destination"]["mapping_to_destination"]
        configuration = source["configuration"]
        
        if source_type == SourceType.AWS_SESSION_CREDENTIALS:
            session_credentials = aws_session_credential_source.generate_session_credentials(configuration)
            mapped_result = {}
            for item in destination_mapping:
              destination_key_name = item["destination_key_name"]
              result_value_key = item["result_value_key"]
              mapped_result[destination_key_name] = session_credentials[result_value_key]
            
        elif source_type ==  SourceType.SECRETS_MANAGER:
            mapped_result = {}

        elif source_type ==  SourceType.LAMBDA_ENVIRONMENT_VARIABLE:
            mapped_result = {}
        
        destination_values_map.setdefault(destination_specifier,[]).append(mapped_result)
    
    for name, destination_configuration in destinations.items():

        destination_type = destination_configuration["type"]
        mapped_result = destination_values_map[name]

        if destination_type == DestinationType.CIRCLECI_ENVIRONMENT_VARIABLE:
            circleci.update_environment_variables(mapped_result, destination_configuration)
