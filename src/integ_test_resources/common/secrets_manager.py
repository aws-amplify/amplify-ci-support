import base64

import boto3
from botocore.exceptions import ClientError

from common.platforms import Platform


def get_integ_tests_secrets(platform: Platform) -> str:
    secret_name = "{}_integ_tests_secrets".format(platform.value)
    ## using constant region as these secrets are static & created outside of this app
    region_name = "us-east-1"

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        ## secret cannot be retrived. Throw exception and fail
        raise e
    else:
        # Depending on whether the secret is a string or binary, one of these fields will be populated.
        if 'SecretString' in get_secret_value_response:
            secret = get_secret_value_response['SecretString']
            return secret
        else:
            decoded_binary_secret = base64.b64decode(get_secret_value_response['SecretBinary'])
            return decoded_binary_secret
