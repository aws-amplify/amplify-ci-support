from common import *
import json
import os
import uuid

CODEBUILD_SRC_DIR = os.getenv('CODEBUILD_SRC_DIR')
BASE_PATH = os.getenv('HOME') if CODEBUILD_SRC_DIR is None else CODEBUILD_SRC_DIR
PROJECT_DIR = f"{BASE_PATH}/_amplify_project_tmp"


def get_auth_config():
    is_update = True if get_category_config("auth") is not None else False
    if (is_update):
        auth_config_json_element_name = 'serviceModification'
        user_pool_config_json_element_name = 'userPoolModification'
        id_pool_config_json_element_name = 'identityPoolModification'
    else:
        auth_config_json_element_name = 'serviceConfiguration'
        user_pool_config_json_element_name = 'userPoolConfiguration'
        id_pool_config_json_element_name = 'identityPoolConfiguration'

    auth_config = {
        'version': 1,
        'resourceName': 'AndroidIntegTestAuth'
    }
    user_pool_config = {
        'requiredSignupAttributes': ['EMAIL', 'NAME', 'NICKNAME'],
        'signinMethod': 'USERNAME',
        'userPoolGroups': [
            {'groupName': 'Admins'},
            {'groupName': 'Bloggers'},
            {'groupName': 'Moderators'}
        ],
        'writeAttributes': ['EMAIL', 'NAME', 'NICKNAME'],
        'readAttributes': ['EMAIL', 'NAME', 'NICKNAME'],
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
    auth_config[auth_config_json_element_name][
        user_pool_config_json_element_name] = user_pool_config
    auth_config[auth_config_json_element_name][id_pool_config_json_element_name] = id_pool_config
    return auth_config


def config_auth(auth_config):
    cmd = [AMPLIFY_COMMAND,
           "add" if get_category_config('auth') is None else "update",
           "auth",
           "--headless"]
    result = run_command(cmd, input=json.dumps(auth_config))
    return result.returncode


def create_users():
    config = json.load(open(f"{PROJECT_DIR}/app/src/main/res/raw/amplifyconfiguration.json"))
    userPoolId = config['auth']['plugins']['awsCognitoAuthPlugin']['CognitoUserPool']['Default'][
        'PoolId']
    users = [('User_1', str(uuid.uuid1())), ('User_2', str(uuid.uuid4()))]
    credentials = []
    for user in users:
        create_user_cmd = ["aws",
                           "cognito-idp",
                           "admin-create-user",
                           "--user-pool-id", userPoolId,
                           "--username", user[0]]
        run_command(create_user_cmd)
        set_user_password = ["aws",
                             "cognito-idp",
                             "admin-set-user-password",
                             "--user-pool-id", userPoolId,
                             "--username", user[0],
                             "--password", user[1],
                             "--permanent"]
        run_command(set_user_password)
        credentials.append({"username": user[0], "password": user[1]})
    credentials_json = json.dumps({"credentials": credentials})
    credentials_file = open(f"{PROJECT_DIR}/app/src/main/res/raw/credentials.json", 'w')
    credentials_file.write(credentials_json)
    credentials_file.close()






