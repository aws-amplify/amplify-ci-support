import os
import subprocess
import argparse
import boto3
import logging
from enum import Enum

class OperationType(Enum):
    ADD = "add"
    UPDATE = "update"
    REMOVE = "remove"

def parse_arguments():
    parser = argparse.ArgumentParser(description="Utility that runs the Amplify CLI in headless mode to provision backend resources for integration tests.")
    parser.add_argument("--backend_name", help="The name of the Amplify app.", required=True)
    parser.add_argument("--schema_dir", help="Name of the subdirectory under the schemas folder that contains the GraphQL schemas for the backend API.", required=True)
    parser.add_argument("--group_names", help="Comma-separated list of group names to be created.", default="")
    parser.add_argument("--conflict_resolution", help="Conflict resolution mode.")
    parser.add_argument("--log", help="Set the log level.", default='INFO')
    return parser.parse_args()

LOG_FORMATTER = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
CONSOLE_HANDLER = logging.StreamHandler()
CONSOLE_HANDLER.setFormatter(LOG_FORMATTER)
LOGGER = logging.getLogger("AmplifyDeployerUtil")
LOGGER.addHandler(CONSOLE_HANDLER)

AMPLIFY_AWSSDK_CLIENT = boto3.client('amplify')
REGION = 'us-east-1'
SCRIPTS_DIR = os.path.dirname(__file__)
LOGGER.info(f"SCRIPTS_DIR = {SCRIPTS_DIR}")

# If running within CodeBuild, we want to use the value of CODEBUILD_SRC_DIR environment variable as the base path.
# If running on a developer's machine, use the value of the HOME environment variable as the base.
CODEBUILD_SRC_DIR = os.getenv('CODEBUILD_SRC_DIR')
BASE_PATH = os.getenv('HOME') if CODEBUILD_SRC_DIR is None else CODEBUILD_SRC_DIR
LOGGER.info(f"BASE_PATH = {BASE_PATH}")

def run_command(cmd, work_dir:str, input: str = None):
    LOGGER.debug(msg=" ".join(cmd))
    result = subprocess.run(cmd, 
                        text=True,
                        input = input if input is not None else '',
                        cwd = work_dir)
                        # stdout=subprocess.PIPE, 
                        # stderr=subprocess.PIPE)
    return result
