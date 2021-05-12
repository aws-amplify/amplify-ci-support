import os
from enum import Enum
from common import (
    OperationType
)

class ApiAuthMode(Enum):
    NONE: "NONE"
    API_KEY = "API_KEY"
    AWS_IAM = "AWS_IAM"
    OPENID_CONNECT = "OPENID_CONNECT"
    AMAZON_COGNITO_USER_POOLS = "AMAZON_COGNITO_USER_POOLS"


class ApiAuthModeFactory:
    @classmethod
    def create_user_pools_config(cls, auth_resource_name:str):
        return {
            'mode': 'AMAZON_COGNITO_USER_POOLS',
            'cognitoUserPoolId': auth_resource_name
        }

    @classmethod
    def create_api_key_config(cls):
        return { 
            'mode': 'API_KEY',
            'expirationTime': 365
        }

    @classmethod
    def create_oidc_config(cls, client_id: str, issuer_url: str, provider_name: str, is_default: bool = False):
        return { 
            'mode': 'OPENID_CONNECT',
            'openIDClientID': client_id,
            'openIDIssuerURL': issuer_url,
            'openIDProviderName': provider_name 
        }
    
    @classmethod
    def create_iam_config(cls):
        return { 'mode': 'AWS_IAM' }


class ApiConfigFactory:
    name = None
    schema_dir = None
    default_auth_mode = None
    additional_auth_modes = {}
    is_update = False

    @classmethod
    def create(cls, *, api_name:str, 
                        op_type:OperationType, 
                        schema_dir:str, 
                        default_auth_mode:ApiAuthMode, 
                        additional_auth_modes: dict = None,
                        conflict_resolution: str = None  ):
        gql_schema = ""
        for entry in os.listdir(schema_dir):
            if os.path.isfile(os.path.join(schema_dir, entry)):
                with open(os.path.join(schema_dir, entry), "r") as text_file:
                    gql_schema += text_file.read() + "\n"
        api_config = {
            'version': 1
        }
        api_config_json_element_name = 'serviceModification' if op_type == OperationType.UPDATE else 'serviceConfiguration'
        api_config[api_config_json_element_name] = {
            'serviceName': 'AppSync',
            'apiName': api_name,
            'transformSchema': gql_schema,
            'defaultAuthType': default_auth_mode
            
        }
        print(f"conflict resolution = {conflict_resolution}")
        if conflict_resolution is not None:
            api_config[api_config_json_element_name]['conflictResolution'] = {
                'defaultResolutionStrategy': {
                    'type': conflict_resolution
                }
            }
        if additional_auth_modes is not None:
            api_config[api_config_json_element_name]['additionalAuthTypes'] = list(additional_auth_modes.values())

        return api_config  
