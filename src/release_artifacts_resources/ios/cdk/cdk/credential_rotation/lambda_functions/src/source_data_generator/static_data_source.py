import os
from typing import Dict


def retrieve_static_data(configuration: map) -> Dict[str, str]:

    if not configuration:
        raise RuntimeError("Configuration is required to retrieve static data")

    lambda_env_variable = configuration["lambda_env_var_key"]
    static_data = os.environ.get(lambda_env_variable)
    return {"result": static_data}
