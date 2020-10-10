#!/usr/bin/env python3

from aws_cdk import core
from stacks.amplify_deployer_stack import AmplifyDeployer

app = core.App()
TARGET_REGION = app.node.try_get_context("region")
TARGET_ACCOUNT = app.node.try_get_context("account")
if TARGET_ACCOUNT is None or TARGET_REGION is None:
    raise Exception("Context variables region and account are required.")

TARGET_ENV = core.Environment( account=TARGET_ACCOUNT, region=TARGET_REGION)
GITHUB_REPO = 'amplify-ci-support'

BANNER_TEXT = f"AWS Account={TARGET_ACCOUNT} Region={TARGET_REGION}"
SEPARATOR = "-" * len(BANNER_TEXT)

github_owner=app.node.try_get_context("github_owner")
branch=app.node.try_get_context("branch")

print(SEPARATOR)
print(BANNER_TEXT)
print(SEPARATOR)

props = {}
props['cb_project_name'] = "AmplifyAuthScenariosDeployer"
props['buildspec_file_path'] = 'src/integ_test_resources/android/amplify/integration/cdk/scripts/buildspec.yml'
props['github_repo'] = GITHUB_REPO
if github_owner is not None:
    props['github_owner'] = github_owner
if branch is not None:
    props['branch'] = branch

AmplifyDeployer(app, "AtAuthTestBackend", props, env=TARGET_ENV)

app.synth()
