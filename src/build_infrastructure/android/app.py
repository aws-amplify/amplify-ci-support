#!/usr/bin/env python3

import os
from aws_cdk import core
from cdk_build_pipeline.build_pipeline_stack import BuildPipelineStack

app = core.App()
TARGET_REGION = app.node.try_get_context("region")
TARGET_ACCOUNT = app.node.try_get_context("account")
TARGET_ENV=core.Environment( account=TARGET_ACCOUNT, region=TARGET_REGION)

print(f"AWS Account={TARGET_ACCOUNT} Region={TARGET_REGION}")

pipeline_stack = BuildPipelineStack(app, 
                                    "AndroidBuildPipeline",
                                    {'pipeline_name':'amplify-android-pipeline', 'codebuild_project_name':'amplify-android-gradle-build'},
                                    env=TARGET_ENV)

app.synth()
