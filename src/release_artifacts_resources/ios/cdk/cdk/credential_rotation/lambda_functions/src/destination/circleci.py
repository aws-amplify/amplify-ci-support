
import os
import boto3
import requests
from src.utils.retry import retry

CIRCLECI_URL_TEMPLATE = "https://circleci.com/api/v2/project/gh/{project_path}/envvar"
DEFAULT_REGION = "us-west-2"

# Provided by Lambda
REGION = os.environ.get("AWS_REGION", DEFAULT_REGION)

def update_environment_variables(variables: map, configuration: map, secretsmanager=None):
    
    if not configuration:
        raise RuntimeError("Configuration is required to update circleci environment")

    github_path = configuration["github_path"]
    secret_arn_env_variable_key = configuration["secret_arn_env_variable"]
    secret_key = os.environ.get(secret_arn_env_variable_key)

    secretsmanager_client = secretsmanager or boto3.client("secretsmanager", region_name=REGION)
    circleci_api_token = get_secret_value(
        secret_key, 
        secretsmanager=secretsmanager_client
        )

    for key, value in variables.items():
        update_env_vars(
            env_var_name=key, 
            env_var_value=value, 
            token=circleci_api_token, 
            project_path=github_path
            )


def get_secret_value(key: str, *, secretsmanager) -> str:
    response = secretsmanager.get_secret_value(SecretId=key)
    api_key = response["SecretString"]
    return api_key


@retry()
def update_env_vars(env_var_name: str, env_var_value: str, token: str, project_path: str):
    url = CIRCLECI_URL_TEMPLATE.format(project_path=project_path)
    headers = {"Circle-Token": token}
    payload = {"name": env_var_name, "value": env_var_value}
    response = requests.post(url, json=payload, headers=headers)
    if not is_successful_response(response):
        safe_content = response.text.replace(env_var_value, "*" * len(env_var_value))

        raise RuntimeError(
            "Could not update env var "
            + f"key={env_var_name} "
            + f"status_code={response.status_code} "
            + f"body={safe_content}"
        )


def is_successful_response(response):
    return response.status_code == 200 or response.status_code == 201
