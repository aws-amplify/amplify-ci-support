"""Utilities to update CircleCI environment variables

This module propagates values to CircleCI environment variables. In the
CircleCI V2 API, permissions are managed via API tokens tied to a specific
user, and environment variables are stored per project.

**Prerequisites for storing environment variables in CircleCI**
- A **GitHub User** with `Write` permissions to a **GitHub Repo**. This should
  be a repo-specific "bot" user--that is, the user should have permissions to
  only the repo being updated.
- A **CircleCI API token** with `Admin` permissions, created by authenticating
  in CircleCI as that GitHub User

**Flow**

The actual process is quite simple

1. This Lambda function retrieves the **CircleCI API token** from AWS Secrets
   Manager
2. The Lambda function invokes the CircleCI V2 API endpoint to update
   environment variables, authenticating with the **CircleCI API token**
"""
import requests
from src.utils.retry import retry
from src.utils.secrets_manager_helper import retrieve_secret

CIRCLECI_URL_TEMPLATE = "https://circleci.com/api/v2/project/gh/{project_path}/envvar"


def update_environment_variables(variables: map, configuration: map):
    """Updates CircleCI environment variables

    Args:
        variables:
            <list expected keys & values>
        configuration:
            <list expected keys & values>

    Raises
        KeyError: if `configuration` does not contain the expected keys
        ValueError: if `configuration` is `None`, or if any required Lambda environment
        variables are missing.
    """
    if not configuration:
        raise RuntimeError("Configuration is required to update CircleCI environment variables")

    github_path = configuration["github_path"]
    circleci_api_token_secret_id_lambda_env_var_key = configuration[
        "circleci_api_token_secret_id_lambda_env_var_key"
    ]
    circleci_api_token = retrieve_secret(circleci_api_token_secret_id_lambda_env_var_key)

    for key, value in variables.items():
        update_env_vars(
            env_var_name=key,
            env_var_value=value,
            token=circleci_api_token,
            project_path=github_path,
        )


def get_secret_value(secret_id: str, *, secretsmanager) -> str:
    response = secretsmanager.get_secret_value(SecretId=secret_id)
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
