#!/usr/bin/env python3

import os
from aws_cdk import (
    core,
    aws_codepipeline_actions
)

from stacks.build_pipeline_stack import AmplifyAndroidCodePipeline
from stacks.github_reporting_stack import GithubReporting
from sources.amplify_android_repo import AmplifyAndroidRepo

app = core.App()
TARGET_REGION = app.node.try_get_context("region")
TARGET_ACCOUNT = app.node.try_get_context("account")
TARGET_ENV=core.Environment( account=TARGET_ACCOUNT, region=TARGET_REGION)

github_owner=app.node.try_get_context("github_owner")
branch=app.node.try_get_context("branch")
df_project_arn = app.node.try_get_context("df_project_arn")
df_device_pool_arn = app.node.try_get_context("df_device_pool_arn")
config_source_bucket = app.node.try_get_context("config_source_bucket")
print(f"AWS Account={TARGET_ACCOUNT} Region={TARGET_REGION}")
log_level=app.node.try_get_context("log_level")


# Currently, device pool arn comes from the CDK context. 
# DeviceFarm project arn and id can be passed in (if using an existing one)
#   or if it's not provided, a new DeviceFarm project will be created.
code_pipeline_stack_props = {
    # If set, config files for tests will be copied from S3. Otherwise, it will attempt to retrieve using the Amplify CLI
    'config_source_bucket': config_source_bucket, 
    'github_source': AmplifyAndroidRepo(owner_override=github_owner, branch_override=branch),
    'device_farm_project_arn': df_project_arn,
    'device_farm_project_id': df_project_arn.split(":")[6] if df_project_arn is not None else None,
    'device_farm_pool_arn': df_device_pool_arn,
    'device_farm_project_name': 'AmplifyAndroidDeviceFarmTests'
}



pipeline_stack = AmplifyAndroidCodePipeline(app, 
                                    "AndroidBuildPipeline",
                                    code_pipeline_stack_props,
                                    description="CI Pipeline assets for amplify-android",
                                    env=TARGET_ENV)
                                    
github_reporting_stack_props = {
    'code_build_project_name': pipeline_stack.get_codebuild_project_name(),
    'oauth_token_secret_name_override': None,
    'log_level': log_level
}

github_reporting_stack = GithubReporting(app, 
                                    "AndroidBuildPipelineGithubReporting", 
                                    github_reporting_stack_props,
                                    description="App from serverless repo that reports build status back to Github",
                                    env=TARGET_ENV)
github_reporting_stack.add_dependency(pipeline_stack)
app.synth()
