import boto3
import os
from typing import Dict, Tuple
from src.utils.retry import retry
from time import sleep
from datetime import datetime

DEFAULT_REGION = "us-west-2"

# Make sure this is at least 2 hours longer than the key rotation schedule set up in the CFn.
# Currently, "2 hours" is an arbitrary value based on the fact that a few of our deployments
# take ~2 hour to run, so we want to leave sufficient time for executing the tests in cases where a
# test is invoked with session credentials created with access keys that are rotated immediately
# thereafter.
SESSION_DURATION_SECONDS = 14400  # 4 hours

# Provided by Lambda
REGION = os.environ.get("AWS_REGION", DEFAULT_REGION)

def generate_session_credentials(
    configuration: map, 
    destination_mapping: list, 
    iam=None, 
    sts=None
    ) -> Dict[str, str]:

    if not configuration:
        raise RuntimeError("Configuration is required to generate session credentials")

    if not destination_mapping:
        raise RuntimeError("Destination mapping is required to generate session credentials")
    
    iam_user_key = configuration["user_env_variable"]
    iam_role_key = configuration["iam_role_env_variable"]
    iam_username = os.environ.get(iam_user_key)
    iam_role = os.environ.get(iam_role_key)
    
    user_credentials: Tuple[str, str] = ()
    session_credentials: Dict[str, str] = {}
    
    try:
        
        iam_client = iam or boto3.client("iam", region_name=REGION)
        user_credentials = create_user_credentials(iam_username, iam=iam_client)
        wait_for_user_credentials()
        temp_credentials = get_session_credentials(user_credentials, role_arn=iam_role, sts=sts)
        
        for item in destination_mapping:
            destination_key_name = item["destination_key_name"]
            result_value_key = item["result_value_key"]
            session_credentials[destination_key_name] = temp_credentials[result_value_key]
    
    finally:
        if user_credentials:
            iam_client.delete_access_key(UserName=iam_username, AccessKeyId=user_credentials[0])
    return session_credentials

def create_user_credentials(username: str, *, iam) -> Tuple[str, str]:
    response = iam.create_access_key(UserName=username)
    access_key_id = response["AccessKey"]["AccessKeyId"]
    secret_access_key = response["AccessKey"]["SecretAccessKey"]
    return access_key_id, secret_access_key


def wait_for_user_credentials():
    """
    Although the key creation via IAM immediately returns credentials, it takes a little time
    (on the order of ~10s) before the key is propagated widely enough to allow it to be used in an
    sts:AssumeRole call. Unfortunately, there isn't a good way to test for the propagation other
    than simply trying to use them, but in practice we haven't seen these become available any
    sooner than ~8s after creation.
    The get_session_credentials call is wrapped in a @retry, so even if this hardcoded timeout isn't
    quite long enough, the subsequent downstream calls will still gracefully handle propagation
    delay.
    """
    sleep(10)


@retry()
def get_session_credentials(credentials: Tuple[str, str], *, role_arn, sts, now=None) -> Dict[str, str]:
    if not sts:
        sts = boto3.client(
            "sts",
            aws_access_key_id=credentials[0],
            aws_secret_access_key=credentials[1],
        )

    now = now or datetime.now()
    timestamp = now.strftime("%Y%m%d%H%M%S")

    response = sts.assume_role(
        RoleArn=role_arn,
        RoleSessionName=f"CredentialRotationLambda-{timestamp}",
        DurationSeconds=SESSION_DURATION_SECONDS,
    )
    return response["Credentials"]
