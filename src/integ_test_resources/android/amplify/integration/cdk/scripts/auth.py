import os
from common import OperationType

class AuthConfigFactory:
    @classmethod
    def create(cls, *, auth_resource_name:str, 
                        identity_pool_name:str,
                        op_type:OperationType,
                        allow_unauth = True,
                        signin_method = 'USERNAME',
                        group_names = [],
                        refresh_token_period_in_days = 365,
                        required_signup_attributes = ['EMAIL', 'NAME', 'NICKNAME'],
                        write_attributes = ['EMAIL', 'NAME', 'NICKNAME'],
                        read_attributes = ['EMAIL', 'NAME', 'NICKNAME']):
        if(OperationType.UPDATE == op_type):
            auth_config_json_element_name = 'serviceModification'
            user_pool_config_json_element_name = 'userPoolModification'
            id_pool_config_json_element_name = 'identityPoolModification'
        else:
            auth_config_json_element_name = 'serviceConfiguration'
            user_pool_config_json_element_name = 'userPoolConfiguration'
            id_pool_config_json_element_name = 'identityPoolConfiguration'

        groups = list(map(lambda group_name: { 'groupName': group_name }, group_names))

        auth_config = {
            'version': 1,
            'resourceName': auth_resource_name
        }
        user_pool_config = {
            'requiredSignupAttributes': required_signup_attributes,
            'signinMethod': signin_method,
            'userPoolGroups': groups,
            'writeAttributes': write_attributes,
            'readAttributes': read_attributes,
            'refreshTokenPeriod': refresh_token_period_in_days
        }

        id_pool_config = {
            'unauthenticatedLogin': allow_unauth,
            'identityPoolName': identity_pool_name
        }
        
        auth_config[auth_config_json_element_name] = {
            'serviceName': 'Cognito',
            'includeIdentityPool': True
        }
        auth_config[auth_config_json_element_name][user_pool_config_json_element_name] = user_pool_config
        auth_config[auth_config_json_element_name][id_pool_config_json_element_name] = id_pool_config

        return auth_config

