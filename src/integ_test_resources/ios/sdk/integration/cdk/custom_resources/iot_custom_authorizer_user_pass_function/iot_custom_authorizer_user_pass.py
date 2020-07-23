import json
import base64
import os

def handler(event, __):
    print(f"### handler: {event}")
    token = event["token"].lower()

    mqtt_user = event["protocolData"]["mqtt"]["username"]
    ios_token = os.environ["custom_auth_user_pass_username"]

    expected_password = os.environ["custom_auth_user_pass_password"]
    password = event["protocolData"]["mqtt"]["password"]
    base64_decoded = base64.b64decode(password).decode("utf-8")
    passwordMatches = expected_password == base64_decoded

    effect = "Allow" if token == "allow" and mqtt_user.startswith(ios_token) and passwordMatches else "Deny"

    response = make_auth_response(effect)
    response_string = json.dumps(response)
    print(f"### returning response: {response_string}")
    return response_string


def make_auth_response(effect):
    resource_arn = os.environ.get("RESOURCE_ARN", "*")
    response = {
        "isAuthenticated": True,
        "principalId": "somePrincipalId",
        "disconnectAfterInSeconds": 3600,
        "refreshAfterInSeconds": 600,
        "policyDocuments": [
            {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Action": ["iot:Connect", "iot:Subscribe", "iot:Publish", "iot:Receive"],
                        "Effect": effect,
                        "Resource": resource_arn,
                    }
                ],
            }
        ],
    }
    return response
