import os
import json
import subprocess
import boto3

AMPLIFY_AWSSDK_CLIENT = boto3.client('amplify')
REGION = 'us-east-1'
PROJECT_NAME = f"amplifyandroidinteg"
ENVIRONMENT = 'integtest'
SCRIPTS_DIR = os.path.dirname(__file__)
print(f"SCRIPTS_DIR = {SCRIPTS_DIR}")

# If running within CodeBuild, we want to use the value of CODEBUILD_SRC_DIR environment variable as the base path.
# If running on a developer's machine, use the value of the HOME environment variable as the base.
CODEBUILD_SRC_DIR = os.getenv('CODEBUILD_SRC_DIR')
BASE_PATH = os.getenv('HOME') if CODEBUILD_SRC_DIR is None else CODEBUILD_SRC_DIR
print(f"BASE_PATH = {BASE_PATH}")

PROJECT_DIR = f"{BASE_PATH}/_amplify_project_tmp"
print(f"Amplify project dir = {PROJECT_DIR}")

AMPLIFY_COMMAND = "amplify"
AMPLIFY_ACTION_PULL = "pull"
AMPLIFY_ACTION_INIT = "init"

AMPLIFY_PROVIDER_CONFIG = {
    'awscloudformation': {
        'configLevel': 'general',
        'region': 'us-east-1'
    }
}

AMPLIFY_FRONTEND_CONFIG = {
    'frontend': 'android',
    'config' : {
        'ResDir': f"app/src/main/res"
    }
}

AMPLIFY_CONFIG = {
    'projectName': PROJECT_NAME,
    'envName': ENVIRONMENT,
    'defaultEditor': 'code'
}

AMPLIFY_CODEGEN_CONFIG = {
    'generateCode': True,
    'codeLanguage': 'java',
    'generateDocs': True
}

def get_existing_app_id():
    try:
        response = AMPLIFY_AWSSDK_CLIENT.list_apps()
        existing_app_id = next(app for app in response['apps'] if app['name'] == PROJECT_NAME)
        return existing_app_id
    except StopIteration:
        print(f"Unable to find existing Amplify app for {PROJECT_NAME}")
        return None

def initialize_new_app():
    init_cmd = [AMPLIFY_COMMAND, 
                AMPLIFY_ACTION_INIT, 
                "--amplify", json.dumps(AMPLIFY_CONFIG), 
                "--providers", json.dumps(AMPLIFY_PROVIDER_CONFIG), 
                "--frontend", json.dumps(AMPLIFY_FRONTEND_CONFIG)]
    result = run_command(init_cmd)
    return result.returncode


def pull_existing_app(existing_app_id):
    amplify_params = AMPLIFY_CONFIG.copy()
    amplify_params.update({'appId': existing_app_id})
    pull_cmd = [AMPLIFY_COMMAND, 
                AMPLIFY_ACTION_PULL, 
                "--amplify", json.dumps(amplify_params), 
                "--providers", json.dumps(AMPLIFY_PROVIDER_CONFIG), 
                "--frontend", json.dumps(AMPLIFY_FRONTEND_CONFIG),
                "--yes"]
    result = run_command(pull_cmd)
    return result.returncode

def get_category_config(category_name: str):
    with open(f"{PROJECT_DIR}/amplify/backend/amplify-meta.json") as amplify_meta_file:
        amplify_meta_content = json.load(amplify_meta_file)
        category_config = amplify_meta_content[category_name] if category_name in amplify_meta_content else None
    return category_config

def push():
    push_cmd = [AMPLIFY_COMMAND,
                "push",
                "--codegen", json.dumps(AMPLIFY_CODEGEN_CONFIG),
                "--yes"]
    result = run_command(push_cmd)
    return result.returncode

def run_command(cmd, input: str = None):
    result = subprocess.run(cmd, 
                        text=True,
                        input = input if input is not None else '',
                        cwd=PROJECT_DIR)
                        # stdout=subprocess.PIPE, 
                        # stderr=subprocess.PIPE)
    return result
