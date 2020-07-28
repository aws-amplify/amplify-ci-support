import boto3
import os
# Note: Make this dynamic if there is more than one custom authorizer in the stack

def on_event(event, __):
    print(f"### on_event({event})")
    request_type = event["RequestType"]
    if request_type == "Create":
        return on_create_or_update(event)
    if request_type == "Update":
        return on_create_or_update(event)
    if request_type == "Delete":
        return on_delete(event)
    raise Exception("Invalid request type: %s" % request_type)


def on_create_or_update(event):
    print(f"### on_create_or_update({event})")
    physical_id = os.environ["custom_auth_user_pass_uuid"]
    custom_authorizer_function_arn = event["ResourceProperties"]["authorizer_function_arn"]
    custom_authorizer_name = event["ResourceProperties"]["authorizer_name"]
    public_key = event["ResourceProperties"]["public_key"]
    token_key_name = event["ResourceProperties"]["token_key_name"]
    create_authorizer(
        custom_authorizer_name, custom_authorizer_function_arn, public_key, token_key_name
    )

    # Creating a domain config is required for enhanced user auth
    beta_endpoint_addr = create_or_update_domainConfig()
    response = {
        "PhysicalResourceId": physical_id,
        "Data": {"BetaEndpointAddress": beta_endpoint_addr},
    }
    print(f"### on_create_or_update response: {response}")
    return response


def create_or_update_domainConfig():
    client = boto3.client("iot")
    default_authorizer_name = os.environ["custom_auth_user_pass_default_authorizer_name"]
    domain_configuration_name = os.environ["custom_auth_user_pass_domain_configuration_name"]

    try:
        create_domain_configuration_response = client.create_domain_configuration(
            domainConfigurationName=domain_configuration_name
        )
        print(f"### create_domain_configuration response: {create_domain_configuration_response}")
    except client.exceptions.ResourceAlreadyExistsException as e:
        print("Already defined, continuing")

    update_domain_configuration_response = client.update_domain_configuration(
        domainConfigurationName=domain_configuration_name,
        domainConfigurationStatus="ENABLED",
        authorizerConfig={"defaultAuthorizerName": default_authorizer_name},
    )
    print(f"### update_domain_configuration response: {update_domain_configuration_response}")

    describe_domain_configuration_response = client.describe_domain_configuration(
        domainConfigurationName=domain_configuration_name
    )
    print(f"### describe_domain_configuration response: {describe_domain_configuration_response}")

    beta_endpoint_addr = describe_domain_configuration_response["domainName"]
    print(f"### beta_endpoint_addr: {beta_endpoint_addr}")

    return beta_endpoint_addr


def on_delete(event):
    print(f"### on_delete({event})")
    physical_id = os.environ["custom_auth_user_pass_uuid"]
    custom_authorizer_name = event["ResourceProperties"]["authorizer_name"]
    delete_authorizer(custom_authorizer_name)
    response = {"PhysicalResourceId": physical_id}
    print(f"### on_delete response: {response}")
    return response


def create_authorizer(name, function_arn, public_key, token_key_name):
    print(f"### create_authorizer({name, function_arn, public_key, token_key_name})")
    client = boto3.client("iot")
    formatted_key = format_public_key(public_key)
    create_authorizer_response = client.create_authorizer(
        authorizerName=name,
        authorizerFunctionArn=function_arn,
        tokenKeyName=token_key_name,
        status="ACTIVE",
        signingDisabled=False,
        tokenSigningPublicKeys={"public_key": formatted_key},
    )
    print(f"### create_authorizer_response: {create_authorizer_response}")


def format_public_key(public_key):
    return f"-----BEGIN PUBLIC KEY-----\n{public_key}\n-----END PUBLIC KEY-----"


def delete_authorizer(name):
    print(f"### delete_authorizer({name})")
    client = boto3.client("iot")
    domain_configuration_name = os.environ["custom_auth_user_pass_domain_configuration_name"]

    client.update_domain_configuration(
        domainConfigurationName=domain_configuration_name, domainConfigurationStatus="DISABLED"
    )
    # It would be nice to clean this stuff up, but this will always fail because you will get an error of:
    # Failed to delete resource. Error: An error occurred (InvalidRequestException) when calling the DeleteDomainConfiguration operation: AWS Managed Domain Configuration must be disabled for at least 7 days before it can be deleted
    # delete_domain_configuration_response = client.delete_domain_configuration(domainConfigurationName="aws_test_iot_custom_authorizer_user_pass")

    update_authorizer_response = client.update_authorizer(authorizerName=name, status="INACTIVE")
    print(f"### update_authorizer_response: {update_authorizer_response}")

    delete_authorizer_response = client.delete_authorizer(authorizerName=name)
    print(f"### delete_authorizer_response: {delete_authorizer_response}")
