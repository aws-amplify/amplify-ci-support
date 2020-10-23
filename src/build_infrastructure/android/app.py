#!/usr/bin/env python3

import os
from aws_cdk import (
    core,
    aws_codepipeline_actions
)

from stacks.device_farm_bootstrap_stack import DeviceFarmBootstrap
from stacks.build_pipeline_stack import AmplifyAndroidCodePipeline

from sources.amplify_android_repo import AmplifyAndroidRepo

app = core.App()
TARGET_REGION = app.node.try_get_context("region")
TARGET_ACCOUNT = app.node.try_get_context("account")
TARGET_ENV=core.Environment( account=TARGET_ACCOUNT, region=TARGET_REGION)

github_owner=app.node.try_get_context("github_owner")
branch=app.node.try_get_context("branch")
df_project_arn = app.node.try_get_context("df_project_arn")
df_device_pool_arn = app.node.try_get_context("df_device_pool_arn")
print(f"AWS Account={TARGET_ACCOUNT} Region={TARGET_REGION}")


# bootstrap_stack_props = {
#     'device_farm_project_name': 'Amplify Android instrumented tests'
# }
# bootstrap_stack = DeviceFarmBootstrap(app, 
#                                     "DeviceFarmBootstrap", 
#                                     props=bootstrap_stack_props, 
#                                     env=TARGET_ENV)

# Need to get DF parameters from custom resource. Having trouble with that right now.
code_pipeline_stack_props = {
    'github_source': AmplifyAndroidRepo(owner_override=github_owner, branch_override=branch),
    'device_farm_project_arn': df_project_arn,
    'device_farm_project_id': df_project_arn.split(":")[6],
    'device_farm_pool_arn': df_device_pool_arn,
    'device_farm_project_name': 'AmplifyAndroidDeviceFarmTests'
}

pipeline_stack = AmplifyAndroidCodePipeline(app, 
                                    "AndroidBuildPipeline",
                                    code_pipeline_stack_props,
                                    env=TARGET_ENV)
# pipeline_stack.add_dependency(bootstrap_stack)
app.synth()
