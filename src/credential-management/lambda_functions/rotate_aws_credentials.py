import boto3
import json
import os
import random
import requests
from time import sleep
from typing import Dict, Tuple

CIRCLECI_BASE_URL = "https://circleci.com/api/v2/project"
CIRCLECI_TOKEN_KEY = "circle-token"
MAX_RETRY_ATTEMPTS = 15
MAX_RETRY_WAIT = 10
SESSION_DURATION_SECONDS = 28800  # 8 hours

CIRCLECI_CONFIG_SECRET = os.environ.get("CIRCLECI_CONFIG_SECRET")
IAM_USERNAME = os.environ.get("IAM_USERNAME")
REPO = os.environ.get("REPO")

random.seed()

"""
A Lambda function to create temporary credentials for a previously-created IAM
user, and propagate them into a CircleCI project's environment variables.
"""


def handler(
    event,
    context,
    *,
    iam=boto3.client("iam"),
    sts=None,
    secretsmanager=boto3.client("secretsmanager"),
):
    try:
        credentials = create_credentials(IAM_USERNAME, iam=iam)
        temporary_credentials = create_temporary_credentials(credentials, sts=sts)
        token = get_secret_value(
            CIRCLECI_CONFIG_SECRET, CIRCLECI_TOKEN_KEY, secretsmanager=secretsmanager
        )
        update_envvars(temporary_credentials, token, REPO)
    finally:
        iam.delete_access_key(UserName=IAM_USERNAME, AccessKeyId=credentials[0])


def create_credentials(username: str, *, iam) -> Tuple[str, str]:
    response = iam.create_access_key(UserName=username)
    access_key_id = response["AccessKey"]["AccessKeyId"]
    secret_access_key = response["AccessKey"]["SecretAccessKey"]

    return (access_key_id, secret_access_key)


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
                        logger(f"{max_attempts} retries failed; bailing")
                        raise

        return retryer

    return wrapper


@retry()
def create_temporary_credentials(
    credentials: Tuple[str, str], *, sts
) -> Dict[str, str]:
    if not sts:
        sts = boto3.client(
            "sts",
            aws_access_key_id=credentials[0],
            aws_secret_access_key=credentials[1],
        )

    response = sts.get_session_token(DurationSeconds=SESSION_DURATION_SECONDS)
    credentials = response["Credentials"]

    return {
        "AWS_ACCESS_KEY_ID": credentials["AccessKeyId"],
        "AWS_SECRET_ACCESS_KEY": credentials["SecretAccessKey"],
        "AWS_SESSION_TOKEN": credentials["SessionToken"],
    }


def get_secret_value(key: str, subkey: str, *, secretsmanager) -> str:
    response = secretsmanager.get_secret_value(SecretId=key)
    config = json.loads(response["SecretString"])

    return config[subkey]


def update_envvars(
    temporary_credentials: Dict[str, str],
    token: str,
    repo: str,
    *,
    max_attempts=MAX_RETRY_ATTEMPTS,
    max_wait=MAX_RETRY_WAIT,
    log=True,
) -> None:
    url = f"{CIRCLECI_BASE_URL}/{repo}/envvar"
    headers = {"Circle-Token": token}

    @retry(max_attempts=max_attempts, max_wait=max_wait, log=log)
    def update(key: str, value: str) -> None:
        payload = {"name": key, "value": value}
        response = requests.post(url, json=payload, headers=headers)

        if response.status_code != 201:
            safe_content = response.content.replace(value, "*" * len(value))

            raise RuntimeError(
                "Could not update envvar "
                + f"key={key} "
                + f"status_code={response.status_code} "
                + f"body={safe_content}"
            )

    for key, value in temporary_credentials.items():
        update(key, value)
