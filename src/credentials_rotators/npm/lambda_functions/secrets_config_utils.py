import logging
import json

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def get_secrets_config():
    """Reads the secrets_config.json into a Dictionary
    Returns:
        The secrets_config.json file as a Dictionary
    Raises:
        IOError, FileNotFoundError: If the secrets configuration file cannot be read
    """
    try:
        with open('secrets_config.json') as config_file:
            config = json.load(config_file)
            return config
    except FileNotFoundError as e:
        # try reading from lambda_functions package (used when accessing from stacks package)
        with open('lambda_functions/secrets_config.json') as config_file:
            config = json.load(config_file)
            return config

def get_secret_config(secret_id):
    """
    Returns the secret configuration of the secret referenced using secret_id in secrets_config.json
    Args:
        secret_id: Identifier for the secret in secrets_config.json
    Raises:
        KeyError: If the required secret is not present in the configuration
    """
    try:
        secret_config = get_secrets_config()[secret_id]
        return secret_config
    except KeyError as e:
        logger.info(f'Invalid configuration. Could not read config for secret {secret_id}')
        raise e

def get_secret_key(secret_config):
    """Gets the key of the secret referenced using secret_config from the secrets_config.json
    Args:
        secret_config (Dictionary): The configuration for the secret specified in secrets_config.json
    Returns:
        The key of the secret as a String
    Raises:
        KeyError: If the secret_key is not present in secret configuration
    """
    try:
        return secret_config['secret_key']
    except KeyError as e:
        logger.info(f'Invalid config object. Could not read secret_key of secret {secret_config}')
        raise e


def get_secret_arn(secret_config):
    """Gets the full arn of the secret referenced using secret_config in the secrets_config.json
    Args:
        secret_config (Dictionary): The configuration for the secret specified in secrets_config.json
    Returns:
        The full arn of the secret as a String
    Raises:
        KeyError: If the arn is not present in secrets_config.json
    """
    try:
        return secret_config['arn']
    except KeyError as e:
        logger.info(f'Invalid config object. Could not read arn from secret configuration {secret_config}')
        raise e

def get_alarm_subscriptions(secret_id):
    """Gets the list of emails to subscribe to cloudwatch alarms from the secret configuration
    Args:
        secret_id (string): The identifier corresponding to the secret in the secrets_config.json file
    Returns:
        The list of emails to subscribe to cloudwatch alarms for the secret rotation
    """
    try:
        return get_secret_config(secret_id)['alarm_subscriptions']
    except KeyError as e:
        logger.info(f'No emails to subscribe for secret with id: {secret_id}')
        return []

def get_access_token_secrets_configs(secret_id):
    """
    Returns the configurations of secrets containing the npm access tokens to be rotated
    Args:
        secret_id (string): The identifier corresponding to the secret in the secrets_config.json file
    Raises:
        KeyError: If the access_token secrets are not present in the config
    """
    try:
        access_token_secrets_configs = get_secret_config(secret_id)['secrets']
        return access_token_secrets_configs
    except KeyError as e:
        logger.info(f'Invalid config object. Could not read configuration for access token secrets for secret: {secret_id}')
        raise e