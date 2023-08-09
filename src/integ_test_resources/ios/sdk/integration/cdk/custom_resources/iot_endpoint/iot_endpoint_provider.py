import boto3


def on_event(event, context):
    request_type = event["RequestType"]
    if request_type == "Create":
        return on_create_or_update(event)
    if request_type == "Update":
        return on_create_or_update(event)
    if request_type == "Delete":
        return on_delete(event)
    raise Exception("Invalid request type: %s" % request_type)


def on_create_or_update(event):
    client = boto3.client("iot")
    describe_endpoint_response = client.describe_endpoint(endpointType="iot:Data-ATS")
    endpoint_address = describe_endpoint_response["endpointAddress"]
    response = {
        "PhysicalResourceId": endpoint_address,
        "Data": {"EndpointAddress": endpoint_address},
    }
    return response


def on_delete(event):
    physical_id = event["PhysicalResourceId"]
    response = {"PhysicalResourceId": physical_id}
    return response
