import json
import os
from common import (
    LOGGER,
    AMPLIFY_AWSSDK_CLIENT,
    SECRETS_MANAGER_CLIENT,
    BASE_PATH,
    run_command,
    OperationType
)
from auth import *

AMPLIFY_COMMAND = "amplify"
AMPLIFY_ACTION_PULL = "pull"
AMPLIFY_ACTION_INIT = "init"
AMPLIFY_ENVIRONMENT = "main" # Static for now

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

AMPLIFY_CODEGEN_CONFIG_ANDROID = {
    'generateCode': True,
    'codeLanguage': 'java',
    'generateDocs': True
}

class AmplifyApp:
    backend_name = None
    app_id = None
    project_dir = None
    amplify_meta_content = None

    def __init__(self, *, backend_name:str):
        self.backend_name = backend_name
        self.project_dir = f"{BASE_PATH}/_amplify_{self.backend_name}"
        os.system(f"mkdir -p {self.project_dir}")
        self.app_id = self._get_existing_app_id()
        if self.app_id is None and self._initialize_new_app() != 0:
            raise Exception("Unable to initialize Amplify project.")
        else:
            self._pull_existing_app()
        with open(f"{self.project_dir}/amplify/backend/amplify-meta.json") as amplify_meta_file:
            self.amplify_meta_content = json.load(amplify_meta_file)
        self._load_metadata()

    def is_category_configured(self, category_name:str):
        if self.amplify_meta_content is None:
            return False
        return category_name in self.amplify_meta_content.keys()

    def config_auth(self, auth_config, op_type:OperationType):
        cmd = [AMPLIFY_COMMAND,
                        op_type.value,
                        "auth",
                        "--headless"]
        result = run_command(cmd, work_dir=self.project_dir, input=json.dumps(auth_config))
        return result.returncode

    def config_api(self, api_config, op_type:OperationType):
        cmd = [AMPLIFY_COMMAND,
                        op_type.value,
                        "api",
                        "--headless"]
        result = run_command(cmd, work_dir=self.project_dir, input=json.dumps(api_config))
        return result.returncode
        
    def get_category_config(self, category_name: str):
        if self.amplify_meta_content is None:
            return None
        return category_name in self.amplify_meta_content.keys()

    def push(self):
        push_cmd = [AMPLIFY_COMMAND,
                    "push",
                    "--codegen", json.dumps(AMPLIFY_CODEGEN_CONFIG_ANDROID),
                    "--yes"]
        result = run_command(push_cmd, self.project_dir)
        self._load_metadata()
        return result.returncode

    def retrieve_secret(self, secret_name: str):
        get_secret_result = SECRETS_MANAGER_CLIENT.get_secret_value(SecretId=secret_name)
        return json.loads(get_secret_result["SecretString"])

    def _get_existing_app_id(self):
        try:
            response = AMPLIFY_AWSSDK_CLIENT.list_apps()
            existing_app_id = next(app['appId'] for app in response['apps'] if app['name'] == self.backend_name)
            return existing_app_id
        except StopIteration:
            LOGGER.error(f"Unable to find existing Amplify app for {self.backend_name}")
            return None

    def _initialize_new_app(self):
        init_cmd = [AMPLIFY_COMMAND, 
                    AMPLIFY_ACTION_INIT, 
                    "--amplify", json.dumps(self._get_amplify_config()), 
                    "--providers", json.dumps(AMPLIFY_PROVIDER_CONFIG), 
                    "--frontend", json.dumps(AMPLIFY_FRONTEND_CONFIG),
                    "--forcePush",
                    "--yes"]
        result = run_command(init_cmd, self.project_dir)
        self.app_id = self._get_existing_app_id()
        return result.returncode


    def _pull_existing_app(self):
        amplify_params = self._get_amplify_config().copy()
        amplify_params.update({'appId': self.app_id})
        pull_cmd = [AMPLIFY_COMMAND, 
                    AMPLIFY_ACTION_PULL, 
                    "--amplify", json.dumps(amplify_params), 
                    "--providers", json.dumps(AMPLIFY_PROVIDER_CONFIG), 
                    "--frontend", json.dumps(AMPLIFY_FRONTEND_CONFIG),
                    "--yes"]
        result = run_command(pull_cmd, self.project_dir)
        return result.returncode

    def _get_amplify_config(self):
        return {
            'projectName': self.backend_name,
            'envName': AMPLIFY_ENVIRONMENT,
            'defaultEditor': 'code'
        }

    def _load_metadata(self):
        with open(f"{self.project_dir}/amplify/backend/amplify-meta.json") as amplify_meta_file:
            self.amplify_meta_content = json.load(amplify_meta_file)
