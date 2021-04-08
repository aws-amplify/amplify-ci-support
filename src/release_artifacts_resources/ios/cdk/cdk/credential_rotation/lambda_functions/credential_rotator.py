import os
import random
from datetime import datetime
from time import sleep
from typing import Dict, Tuple

import boto3
import requests

# Common configurations for all projects
CIRCLECI_URL_TEMPLATE = "https://circleci.com/api/v2/project/gh/{project_path}/envvar"
DEFAULT_REGION = "us-west-2"

# Note that the total duration of MAX_RETRY_ATTEMPTS * MAX_RETRY_WAIT * <# of times retry is used>
# must not exceed the Timeout value set in the CloudFormation (CFn) template, or else this lambda
# will leave unused access keys in the IAM user. It is important to have the retry and timeout
# configured to meaningful values, since key creation takes some time to propagate, and any attempt
# to assume role using the newly created key may fail. Not to mention the usual vagaries of internet
# communication that could benefit from a retry.
MAX_RETRY_ATTEMPTS = 10
MAX_RETRY_WAIT = 10


# Make sure this is at least 2 hours longer than the key rotation schedule set up in the CFn.
# Currently, "2 hours" is an arbitrary value based on the fact that a few of our deployments
# take ~2 hour to run, so we want to leave sufficient time for executing the tests in cases where a
# test is invoked with session credentials created with access keys that are rotated immediately
# thereafter.
SESSION_DURATION_SECONDS = 14400  # 4 hours

# Provided by Lambda
REGION = os.environ.get("AWS_REGION", DEFAULT_REGION)

# Per-project configuration
CIRCLECI_CONFIG_SECRET = os.environ.get("CIRCLECI_CONFIG_SECRET")
CIRCLECI_EXECUTION_ROLE = os.environ.get("CIRCLECI_EXECUTION_ROLE")
IAM_USERNAME = os.environ.get("IAM_USERNAME")
GITHUB_PROJECT_PATH = os.environ.get("GITHUB_PROJECT_PATH")

random.seed()


def handler(event, context, *, iam=None, sts=None, secretsmanager=None):
    iam_client = iam or boto3.client("iam", region_name=REGION)
    secretsmanager_client = secretsmanager or boto3.client("secretsmanager", region_name=REGION)

    user_credentials: Tuple[str, str] = ()
    try:
        user_credentials = create_user_credentials(IAM_USERNAME, iam=iam_client)
        wait_for_user_credentials()
        session_credentials = get_session_credentials(user_credentials, sts=sts)
        circleci_api_token = get_secret_value(
            CIRCLECI_CONFIG_SECRET, secretsmanager=secretsmanager_client
        )
        update_env_vars(session_credentials, circleci_api_token, GITHUB_PROJECT_PATH)
    finally:
        if user_credentials:
            iam_client.delete_access_key(UserName=IAM_USERNAME, AccessKeyId=user_credentials[0])


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


def retry(max_attempts=MAX_RETRY_ATTEMPTS, max_wait=MAX_RETRY_WAIT, log=True):
    def logger(*msgs):
        if log:
            for msg in msgs:
                print(msg)

    def wrapper(func):
        def retryer(*args, **kwargs):
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as ex:
                    logger("Exception caught: ", ex)

                    if attempt != max_attempts:
                        secs = random.uniform(0, min(max_wait, 2 ** attempt))
                        msecs = round(secs * 1000)

                        logger(f"Waiting for {msecs}ms")
                        sleep(secs)
                    else:
                        logger(f"{max_attempts} retries failed; aborting")
                        raise

        return retryer

    return wrapper


@retry()
def get_session_credentials(credentials: Tuple[str, str], *, sts, now=None) -> Dict[str, str]:
    if not sts:
        sts = boto3.client(
            "sts",
            aws_access_key_id=credentials[0],
            aws_secret_access_key=credentials[1],
        )

    now = now or datetime.now()
    timestamp = now.strftime("%Y%m%d%H%M%S")

    response = sts.assume_role(
        RoleArn=CIRCLECI_EXECUTION_ROLE,
        RoleSessionName=f"CredentialRotationLambda-{timestamp}",
        DurationSeconds=SESSION_DURATION_SECONDS,
    )
    session_credentials: Dict[str, str] = response["Credentials"]

    return {
        "XCF_AWS_ACCESS_KEY_ID": session_credentials["AccessKeyId"],
        "XCF_AWS_SECRET_ACCESS_KEY": session_credentials["SecretAccessKey"],
        "XCF_AWS_SESSION_TOKEN": session_credentials["SessionToken"],
    }


def get_secret_value(key: str, *, secretsmanager) -> str:
    response = secretsmanager.get_secret_value(SecretId=key)
    api_key = response["SecretString"]
    return api_key


def update_env_vars(
    temporary_credentials: Dict[str, str],
    token: str,
    project_path: str,
    *,
    max_attempts=MAX_RETRY_ATTEMPTS,
    max_wait=MAX_RETRY_WAIT,
    log=True,
) -> None:
    url = CIRCLECI_URL_TEMPLATE.format(project_path=project_path)
    headers = {"Circle-Token": token}

    @retry(max_attempts=max_attempts, max_wait=max_wait, log=log)
    def update(env_var_name: str, env_var_value: str) -> None:
        payload = {"name": env_var_name, "value": env_var_value}
        response = requests.post(url, json=payload, headers=headers)
        if not is_successful_response(response):
            safe_content = response.text.replace(env_var_value, "*" * len(env_var_value))

            raise RuntimeError(
                "Could not update env var "
                + f"key={env_var_name} "
                + f"status_code={response.status_code} "
                + f"body={safe_content}"
            )

    for key, value in temporary_credentials.items():
        update(key, value)


def is_successful_response(response):
    return response.status_code == 200 or response.status_code == 201
