#!/usr/bin/env python3

import os
from aws_cdk import (
    core,
    aws_codepipeline_actions
)

from stacks.build_pipeline_stack import AmplifyAndroidCodePipeline
from stacks.account_bootstrap_stack import AccountBootstrap

app = core.App()
TARGET_REGION = app.node.try_get_context("region")
TARGET_ACCOUNT = app.node.try_get_context("account")
TARGET_ENV=core.Environment( account=TARGET_ACCOUNT, region=TARGET_REGION)
REPO='amplify-android'

github_owner=app.node.try_get_context("github_owner")
branch=app.node.try_get_context("branch")
config_source_bucket = app.node.try_get_context("config_source_bucket")
print(f"AWS Account={TARGET_ACCOUNT} Region={TARGET_REGION}")
log_level=app.node.try_get_context("log_level")

account_bootstrap = AccountBootstrap(app, "AccountBootstrap", {}, env=TARGET_ENV)

code_pipeline_stack_props = {
    # If set, config files for tests will be copied from S3. Otherwise, it will attempt to retrieve using the Amplify CLI
    'config_source_bucket': account_bootstrap.config_source_bucket.bucket_name, 
    'github_source': { 
        'owner': github_owner, 
        'repo': REPO , 
        'base_branch': branch 
    },
    'device_farm_project_name': 'AmplifyAndroidDeviceFarmTests',
    'codebuild_project_name_prefix': 'AmplifyAndroid'
}

pipeline_stack = AmplifyAndroidCodePipeline(app,
                                    "AndroidBuildPipeline",
                                    code_pipeline_stack_props,
                                    description="CI Pipeline assets for amplify-android",
                                    env=TARGET_ENV)


app.synth()
