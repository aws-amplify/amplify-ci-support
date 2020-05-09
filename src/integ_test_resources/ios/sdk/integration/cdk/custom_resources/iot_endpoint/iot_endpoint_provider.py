import boto3


def on_event(event, context):
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
    client = boto3.client("iot")
    describe_endpoint_response = client.describe_endpoint(endpointType="iot:Data-ATS")
    print(f"### describe_endpoint_response: {describe_endpoint_response}")
    endpoint_address = describe_endpoint_response["endpointAddress"]
    response = {
        "PhysicalResourceId": endpoint_address,
        "Data": {"EndpointAddress": endpoint_address},
    }
    print(f"### on_create_or_update response: {response}")
    return response


def on_delete(event):
    print(f"### on_delete({event})")
    physical_id = event["PhysicalResourceId"]
    print(f"### on_delete, PhysicalResourceId: {physical_id}")
    response = {"PhysicalResourceId": physical_id}
    print(f"### on_delete response: {response}")
    return response
