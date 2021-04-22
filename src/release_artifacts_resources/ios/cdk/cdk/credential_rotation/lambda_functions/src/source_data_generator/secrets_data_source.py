import json
from typing import Dict

from src.utils.secrets_manager_helper import retrieve_secret


def retrieve_secrets(configuration: map) -> Dict[str, str]:

    if not configuration:
        raise RuntimeError("Configuration is required to retrieve secrets")

    secret_key_env_variable = configuration["secret_key_env_variable"]
    secret_value = retrieve_secret(secret_key_env_variable)
    try:
        json_value = json.loads(secret_value)
        return json_value
    except (json.decoder.JSONDecodeError):
        return {"result": secret_value}
