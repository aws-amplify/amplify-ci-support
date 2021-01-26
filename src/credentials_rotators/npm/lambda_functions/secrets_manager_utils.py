import logging
import json
from secrets_config_utils import get_secret_arn, get_secret_key

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def get_secret_dict(service_client, secret_config, stage='AWSCURRENT', token=None):
    """Gets the secret JSON from secrets manager corresponding to the secret stage, and token
    Args:
        service_client (client): The secrets manager service client
        secret_config (Dictionary): The configuration for the secret specified in secrets_config.json
        stage (string): The stage identifying the secret version
        token (string): The ClientRequestToken associated with the secret version, or None if no validation is desired
    Returns:
        Secret as a dictionary
    Raises:
        ResourceNotFoundException: If the specified secret and stage does not exist
        ValueError: If the secret is not valid JSON
    """

    secret_arn = get_secret_arn(secret_config)
    # Only do VersionId validation against the stage if a token is passed in
    if token:
        secret = service_client.get_secret_value(SecretId=secret_arn, VersionId=token, VersionStage=stage)
    else:
        secret = service_client.get_secret_value(SecretId=secret_arn, VersionStage=stage)
    plaintext = secret['SecretString']

    # Parse and return the secret JSON string
    secret_dict = json.loads(plaintext)
    return secret_dict

def get_secret_value(service_client, secret_config, stage='AWSCURRENT', token=None):
    """Gets the secret value corresponding to the secret_key for secret referenced by secret_config in the secrets_config.json
    Args:
        service_client (client): The secrets manager service client
        secret_config (string): The identifier corresponding to the secret in the secrets_config.json file
        stage (string): The stage identifying the secret version
        token (string): The ClientRequestToken associated with the secret version, or None if no validation is desired
    Returns:
        The Value of the secret
    Raises:
        KeyError: If the secret_key is not present in secret_dict
        ResourceNotFoundException: If the specified secret and stage does not exist
        ValueError: If the secret is not valid JSON
    """
    secret_dict = get_secret_dict(service_client, secret_config, stage=stage, token=token)
    try:
        return secret_dict[get_secret_key(secret_config)]
    except KeyError as e:
        logger.info(f'Could not find the secret_key in secret {secret_config}')
        raise e
