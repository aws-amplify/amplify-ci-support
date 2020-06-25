import json
import os


def handler(event, __):
    print(f"### handler: {event}")
    token = event["token"].lower()
    effect = "Allow" if token == "allow" else "Deny"
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
