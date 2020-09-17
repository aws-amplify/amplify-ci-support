#!/usr/bin/env python3

from aws_cdk import core
from stacks.amplify_deployer_stack import AmplifyDeployer

app = core.App()
TARGET_REGION = app.node.try_get_context("region")
TARGET_ACCOUNT = app.node.try_get_context("account")
TARGET_ENV=core.Environment( account=TARGET_ACCOUNT, region=TARGET_REGION)
github_repo=app.node.try_get_context("github_repo")
if github_repo is None:
    raise "github_repo context parameter is required."
github_owner=app.node.try_get_context("github_owner")
branch=app.node.try_get_context("branch")

print(f"AWS Account={TARGET_ACCOUNT} Region={TARGET_REGION}")

props = {}
props['project_name'] = "AmplifyAndroidIntegTestDeployer"
props['github_repo'] = github_repo
if github_owner is not None:
    props['github_owner'] = github_owner
if branch is not None:
    props['branch'] = branch

AmplifyDeployer(app, "AndroidIntegTestInfraDeployer", props, env=TARGET_ENV)

app.synth()