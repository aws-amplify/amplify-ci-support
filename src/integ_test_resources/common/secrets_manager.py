import json

import boto3

from common.platforms import Platform


def get_integ_tests_secrets(platform: Platform) -> dict:
    secret_name = "integ_test_secrets_{}".format(platform.value)
    # using constant region as these secrets are static & created outside of this app
    region_name = "us-east-1"

    session = boto3.session.Session()
    client = session.client(service_name="secretsmanager", region_name=region_name)

    get_secret_value_response = client.get_secret_value(SecretId=secret_name)

    if "SecretString" not in get_secret_value_response:
        raise ValueError(f"Value of {secret_name} is not a string")

    secret_string = get_secret_value_response["SecretString"]
    secret_dict = json.loads(secret_string)
    return secret_dict
