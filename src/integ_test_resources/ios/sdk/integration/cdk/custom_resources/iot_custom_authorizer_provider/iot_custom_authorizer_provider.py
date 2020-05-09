import boto3

# Note: Make this dynamic if there is more than one custom authorizer in the stack
physical_id = "iot_custom_authorizer_provider_20200508074521"


def on_event(event, context):
    print(f"### Event: {event}")
    request_type = event["RequestType"]
    if request_type == "Create":
        return on_create_or_update(event)
    if request_type == "Update":
        return on_create_or_update(event)
    if request_type == "Delete":
        return on_delete(event)
    raise Exception("Invalid request type: %s" % request_type)


def on_create_or_update(event):
    try:
        print(f"### on_create_or_update")
        custom_authorizer_arn = event["ResourceProperties"]["authorizer_arn"]
        custom_authorizer_name = event["ResourceProperties"]["authorizer_name"]
        public_key = event["ResourceProperties"]["public_key"]
        token_key_name = event["ResourceProperties"]["token_key_name"]
        create_authorizer(custom_authorizer_name, custom_authorizer_arn, public_key, token_key_name)
        response = {"PhysicalResourceId": physical_id}
        print(f"### on_create_or_update returning response: {response}")
        return response
    except Exception as e:
        print(f"### on_create_or_update exception: {e}")
        raise e


def on_delete(event):
    try:
        print(f"### on_delete")
        custom_authorizer_name = event["ResourceProperties"]["authorizer_name"]
        delete_authorizer(custom_authorizer_name)
        response = {"PhysicalResourceId": physical_id}
        print(f"### on_delete returning response: {response}")
        return response
    except Exception as e:
        print(f"### on_delete exception: {e}")
        raise e


def create_authorizer(name, function_arn, public_key, token_key_name):
    print(f"### create_authorizer")
    client = boto3.client("iot")
    create_authorizer_response = client.create_authorizer(
        authorizerName=name,
        authorizerFunctionArn=function_arn,
        tokenKeyName=token_key_name,
        status="ACTIVE",
        signingDisabled=False,
        tokenSigningPublicKeys={"public_key": public_key},
    )
    print(f"### create_authorizer_response: {create_authorizer_response}")


def delete_authorizer(name):
    print(f"### delete_authorizer")
    client = boto3.client("iot")

    update_authorizer_response = client.update_authorizer(authorizerName=name, status="INACTIVE")
    print(f"### update_authorizer_response: {update_authorizer_response}")

    delete_authorizer_response = client.delete_authorizer(authorizerName=name)
    print(f"### delete_authorizer_response: {delete_authorizer_response}")
