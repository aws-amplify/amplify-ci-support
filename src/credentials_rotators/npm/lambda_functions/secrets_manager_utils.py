import logging
import json

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def get_secret_dict(service_client, secret_id, stage='AWSCURRENT', token=None):
    """Gets the secret dictionary corresponding to the secret referenced using secret_id from the secrets_config.json, stage, and token
    This helper function gets credentials for the arn and stage passed in and returns the dictionary by parsing the JSON string
    Args:
        service_client (client): The secrets manager service client
        secret_id (string): The identifier corresponding to the secret in the secrets_config.json file
        token (string): The ClientRequestToken associated with the secret version, or None if no validation is desired
        stage (string): The stage identifying the secret version
    Returns:
        Secret as a dictionary
    Raises:
        ResourceNotFoundException: If the specified secret and stage does not exist
        ValueError: If the secret is not valid JSON
    """

    secret_name = get_secret_arn(secret_id)
    # Only do VersionId validation against the stage if a token is passed in
    if token:
        secret = service_client.get_secret_value(SecretId=secret_name, VersionId=token, VersionStage=stage)
    else:
        secret = service_client.get_secret_value(SecretId=secret_name, VersionStage=stage)
    plaintext = secret['SecretString']

    # Parse and return the secret JSON string
    secret_dict = json.loads(plaintext)
    return secret_dict


def get_secret_key(secret_id):
    """Gets the key of the secret referenced using secret_id from the secrets_config.json
    Args:
        secret_id (string): The identifier corresponding to the secret in the secrets_config.json file
    Returns:
        The key of the secret as a String
    Raises:
        KeyError: If the secret_key is not present in config
    """
    with open('secrets_config.json') as config_file:
        config = json.load(config_file)
        try:
            return config[secret_id]['secret_key']
        except KeyError as e:
            logger.info(f'Invalid config object. Could not read secret_key of secret {secret_id}')
            raise e


def get_secret_arn(secret_id):
    """Gets the full arn of the secret referenced using secret_id in the secrets_config.json
    Args:
        secret_id (string): The identifier corresponding to the secret in the secrets_config.json file
    Returns:
        The full arn of the secret as a String
    Raises:
        KeyError: If the arn is not present in secrets_config.json
    """
    with open('secrets_config.json') as config_file:
        config = json.load(config_file)
        try:
            return config[secret_id]['arn']
        except KeyError as e:
            logger.info(f'Invalid config object. Could not read arn of secret {secret_id}')
            raise e


def get_secret_value(service_client, secret_id, stage='AWSCURRENT', token=None):
    """Gets the secret value corresponding to the secret_key for secret referenced by secret_id in the secrets_config.json
    Args:
        service_client (client): The secrets manager service client
        secret_id (string): The identifier corresponding to the secret in the secrets_config.json file
        stage (string): The stage identifying the secret version
        token (string): The ClientRequestToken associated with the secret version, or None if no validation is desired
    Returns:
        The Value of the secret
    Raises:
        KeyError: If the secret_key is not present in secret_dict
        ResourceNotFoundException: If the specified secret and stage does not exist
        ValueError: If the secret is not valid JSON
    """
    secret_dict = get_secret_dict(service_client, secret_id, stage=stage, token=token)
    try:
        return secret_dict[get_secret_key(secret_id)]
    except KeyError as e:
        logger.info(f'Could not find the secret_key in secret {secret_id}')
        raise e
