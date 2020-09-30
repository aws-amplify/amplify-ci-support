import json
import os
from common import *

class ApiConfigBuilder:
    name = None
    schema_dir = None
    default_auth_mode = None
    additional_auth_modes = {}
    is_update = False

    def as_update(self):
        self.is_update = True

    def with_name(self, name: str):
        self.name = name
        return self
    
    def with_schemas_dir(self, schema_dir: str):
        self.schema_dir = schema_dir
        return self

    def with_auth_resource(self, auth_resource_id: str, is_default: bool = False):
        self.auth_resource_id = auth_resource_id
        user_pool_config = {
            'mode': 'AMAZON_COGNITO_USER_POOLS',
            'cognitoUserPoolId': auth_resource_id
        }
        self._add_auth_mode('AMAZON_COGNITO_USER_POOLS', is_default, user_pool_config)
        return self

    def with_api_key(self, is_default: bool = False):
        self._add_auth_mode('API_KEY', is_default, { 'mode': 'API_KEY' })
        return self

    def with_oidc(self, client_id: str, issuer_url: str, provider_name: str, is_default: bool = False):
        self._add_auth_mode('OPENID_CONNECT', is_default, { 'openIDClientID': client_id, 'openIDIssuerURL': issuer_url, 'openIDProviderName': provider_name })
        return self

    def with_iam(self, is_default: bool = False):
        self._add_auth_mode('AWS_IAM', is_default, { 'mode': 'AWS_IAM' })
        return self

    def _add_auth_mode(self, mode_name: str, is_default: bool, mode_config):
        if is_default:
            self.default_auth_mode = mode_config
        else:
            self.additional_auth_modes[mode_name] = mode_config

    def build(self):
        gql_schema = ""
        for entry in os.listdir(self.schema_dir):
            if os.path.isfile(os.path.join(self.schema_dir, entry)):
                with open(os.path.join(self.schema_dir, entry), "r") as text_file:
                    gql_schema += text_file.read() + "\n"
        api_config = {
            'version': 1
        }
        api_config_json_element_name = 'serviceModification' if self.is_update else 'serviceConfiguration'
        api_config[api_config_json_element_name] = {
            'serviceName': 'AppSync',
            'apiName': self.name,
            'transformSchema': gql_schema,
            'defaultAuthType': self.default_auth_mode,
            'additionalAuthTypes': list(self.additional_auth_modes.values())
        }
        return api_config
        

def get_api_config(api_name: str, schemas_dir: str, auth_resource_id: str):
    is_update = True if get_category_config("api") is not None else False
    builder = ApiConfigBuilder().with_name(api_name) \
                            .with_schemas_dir(schemas_dir) \
                            .with_api_key(True) \
                            .with_auth_resource(auth_resource_id) \
                            .with_iam()
    if(is_update):
        builder.as_update()
    
    return builder.build()

def config_api(api_config):
    cmd = [AMPLIFY_COMMAND,
                    "add" if get_category_config("api") is None else "update",
                    "api",
                    "--headless"]
    result = run_command(cmd, input=json.dumps(api_config))
    return result.returncode
