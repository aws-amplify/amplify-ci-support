from common import *
import json
import os
def get_auth_config():
    is_update = True if get_category_config("auth") is not None else False
    if(is_update):
        auth_config_json_element_name = 'serviceModification'
        user_pool_config_json_element_name = 'userPoolModification'
        id_pool_config_json_element_name = 'identityPoolModification'
    else:
        auth_config_json_element_name = 'serviceConfiguration'
        user_pool_config_json_element_name = 'userPoolConfiguration'
        id_pool_config_json_element_name = 'identityPoolConfiguration'

    auth_config = {
        'version': 1,
        'resourceName':'AndroidIntegTestAuth'
    }
    user_pool_config = {
        'requiredSignupAttributes':['EMAIL', 'NAME', 'NICKNAME'],
        'signinMethod':'USERNAME',
        'userPoolGroups': [ 
            { 'groupName': 'Admins' },
            { 'groupName': 'Bloggers' },
            { 'groupName': 'Moderators' }
        ],
        'writeAttributes': ['EMAIL', 'NAME', 'NICKNAME'],
        'readAttributes':['EMAIL', 'NAME', 'NICKNAME'],
        'refreshTokenPeriod': 365
    }
    id_pool_config = {
        'unauthenticatedLogin': True,
        'identityPoolName': 'androididpool'
    }
    
    auth_config[auth_config_json_element_name] = {
        'serviceName': 'Cognito',
        'includeIdentityPool': True
    }
    auth_config[auth_config_json_element_name][user_pool_config_json_element_name] = user_pool_config
    auth_config[auth_config_json_element_name][id_pool_config_json_element_name] = id_pool_config

    return auth_config
    
def config_auth(auth_config):
    cmd = [AMPLIFY_COMMAND,
                    "add" if get_category_config('auth') is None else "update",
                    "auth",
                    "--headless"]
    result = run_command(cmd, input=json.dumps(auth_config))
    return result.returncode
