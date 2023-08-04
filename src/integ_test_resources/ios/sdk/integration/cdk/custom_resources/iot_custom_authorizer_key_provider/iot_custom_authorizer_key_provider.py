import base64

import boto3

"""
Create an asymmetric key pair for 'SIGN_VERIFY' usage, and signs `token_value` with it.

Required permissions:
- kms:CreateKey
- kms:GetPublicKey
- kms:ScheduleKeyDeletion
- kms:Sign
"""

# This is the algorithm recognized by the IoT gateway when verifying token signatures
SIGNING_ALGORITHM = "RSASSA_PKCS1_V1_5_SHA_256"


def on_event(event, __):
    request_type = event["RequestType"]
    if request_type == "Create":
        return on_create(event)
    if request_type == "Update":
        return on_update(event)
    if request_type == "Delete":
        return on_delete(event)
    raise Exception(f"Invalid request type: {request_type}")


def on_create(event):
    token_value = event["ResourceProperties"]["token_value"]
    key_id = create_key()
    return get_create_and_update_response(key_id, token_value)


def on_update(event):
    token_value = event["ResourceProperties"]["token_value"]
    key_id = event["PhysicalResourceId"]
    return get_create_and_update_response(key_id, token_value)


def on_delete(event):
    key_id = event["PhysicalResourceId"]
    delete_key(key_id)
    response = {"PhysicalResourceId": key_id}
    return response


def create_key():
    client = boto3.client("kms")
    create_key_response = client.create_key(
        Description="Key used to sign token values for the IoT custom authorizer",
        KeyUsage="SIGN_VERIFY",
        CustomerMasterKeySpec="RSA_2048",
    )
    key_id = create_key_response["KeyMetadata"]["KeyId"]
    # Newly-created CMKs are enabled by default, so there shouldn't be any need to wait for it to
    # become active before using it.
    return key_id


def get_create_and_update_response(key_id, token_value):
    """
    Gets the public key for `key_id`, and signs `token_value`. Constructs a CustomResource response
    consisting of:
    - PhysicalResourceId: key_id
    - Data:
      - custom_authorizer_public_key: public_key
      - custom_authorizer_token_signature: token_signature

    :param key_id: The key_id to use for signing
    :param token_value: The token to sign
    :return: a CustomResource response
    """
    public_key = get_public_key(key_id)
    token_signature = sign(key_id, token_value)

    response = {
        "PhysicalResourceId": key_id,
        "Data": {
            "custom_authorizer_public_key": public_key,
            "custom_authorizer_token_signature": token_signature,
        },
    }
    return response


def get_public_key(key_id):
    client = boto3.client("kms")
    get_public_key_response = client.get_public_key(KeyId=key_id)
    data = get_public_key_response["PublicKey"]
    base64_bytes = base64.b64encode(data)
    base64_string = base64_bytes.decode("utf8")
    return base64_string


def sign(key_id, token_value):
    client = boto3.client("kms")
    token_bytes = bytes(token_value, "utf8")
    sign_response = client.sign(
        KeyId=key_id,
        Message=token_bytes,
        MessageType="RAW",
        SigningAlgorithm=SIGNING_ALGORITHM,
    )
    data = sign_response["Signature"]
    base64_bytes = base64.b64encode(data)
    base64_string = base64_bytes.decode("utf8")
    return base64_string


def delete_key(key_id):
    client = boto3.client("kms")
    schedule_key_deletion_response = client.schedule_key_deletion(
        KeyId=key_id, PendingWindowInDays=7
    )
