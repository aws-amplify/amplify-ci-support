import json

ECHO_EVENT_VERSION = 2


def handler(event, context):
    print("request: {}".format(json.dumps(event)))

    if "isError" in event and event["isError"]:
        raise AttributeError("Invalid Request")

    event["echoEventVersion"] = ECHO_EVENT_VERSION

    if isProxyRequest(event):
        response = {
            "statusCode": 200,
            "headers": {"Content-Type": "text/plain"},
            "body": json.dumps(event),
            "isBase64Encoded": False,
        }
    else:
        response = event

    return response


def isProxyRequest(event):
    return "resource" in event and "requestContext" in event
