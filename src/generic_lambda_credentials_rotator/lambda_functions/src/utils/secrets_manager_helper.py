import os

import boto3

DEFAULT_REGION = "us-west-2"

# Provided by Lambda
REGION = os.environ.get("AWS_REGION", DEFAULT_REGION)


def retrieve_secret(secret_id_lambda_env_var_key, secretsmanager=None):
    """Retrieve an AWS SecretsManager whose Secret Id is contained in
    the specified Lambda Env Var.
    """

    secretsmanager_client = secretsmanager or boto3.client("secretsmanager", region_name=REGION)
    secret_id = os.environ.get(secret_id_lambda_env_var_key)

    if secret_id is None:
        raise ValueError(f"Lambda env var {secret_id_lambda_env_var_key} is not set")

    return get_secret_value(secret_id, secretsmanager=secretsmanager_client)


def get_secret_value(secret_id: str, *, secretsmanager) -> str:
    response = secretsmanager.get_secret_value(SecretId=secret_id)
    secret_value = response["SecretString"]
    return secret_value
