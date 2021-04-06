#!/usr/bin/env python3

import os
from aws_cdk import (
    core,
    aws_codepipeline_actions
)

from stacks.build_pipeline_stack import AmplifyAndroidCodePipeline
from stacks.account_bootstrap_stack import AccountBootstrap
from stacks.maven_release_stack import MavenReleaseStack

app = core.App()
TARGET_REGION = app.node.try_get_context("region")
TARGET_ACCOUNT = app.node.try_get_context("account")
TARGET_ENV=core.Environment( account=TARGET_ACCOUNT, region=TARGET_REGION)
REPO='amplify-android'

github_owner=app.node.try_get_context("github_owner")
branch=app.node.try_get_context("branch")
config_source_bucket = app.node.try_get_context("config_source_bucket")
release_pr_branch = app.node.try_get_context("release_pr_branch")
log_level=app.node.try_get_context("log_level")

print(f"AWS Account={TARGET_ACCOUNT} Region={TARGET_REGION}")

# Account bootstrap stack
account_bootstrap = AccountBootstrap(app, "AccountBootstrap", {}, env=TARGET_ENV)

# Unit and integration test stack
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

# Maven publisher stack
maven_publisher_stack_props = {
    'github_source': { 
        'owner': github_owner,
        'repo': REPO, 
        'base_branch': branch,
        'release_pr_branch': release_pr_branch
    },
    'codebuild_project_name_prefix': 'AmplifyAndroid'
}

MavenReleaseStack(app, "MavenPublisher", maven_publisher_stack_props, description="Assets used for publishing amplify-android to maven.", env=TARGET_ENV)


app.synth()
