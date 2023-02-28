from common import *
import json
import os
import uuid

STORAGECONFIG = {
    "region": "us-east-1",
    "bucketName": "my-project-bucket"
}

CATEGORIES = {
    "storage": STORAGECONFIG
}


def run_command(cmd, input: str = None):
    result = subprocess.run(cmd,
                            text=True,
                            input=input if input is not None else '',
                            cwd=PROJECT_DIR)
    return result


def config_storage():
    cmd = [AMPLIFY_COMMAND,
           "add",
           "storage",
           "--headless",
           "--categories", json.dumps(CATEGORIES), "--yes"]
    print(str(cmd))
    result = run_command(cmd)
    return result.returncode
