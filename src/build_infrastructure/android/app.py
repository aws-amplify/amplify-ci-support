#!/usr/bin/env python3

import os
from aws_cdk import (
    core,
    aws_codepipeline_actions
)
from sources.amplify_android_repo import AmplifyAndroidRepo
from cdk_build_pipeline.build_pipeline_stack import AmplifyAndroidCodePipeline

app = core.App()
TARGET_REGION = app.node.try_get_context("region")
TARGET_ACCOUNT = app.node.try_get_context("account")
TARGET_ENV=core.Environment( account=TARGET_ACCOUNT, region=TARGET_REGION)

github_owner=app.node.try_get_context("github_owner")
branch=app.node.try_get_context("branch")
print(f"AWS Account={TARGET_ACCOUNT} Region={TARGET_REGION}")
props = {
    'github_source': AmplifyAndroidRepo(owner_override=github_owner, branch_override=branch)
}

pipeline_stack = AmplifyAndroidCodePipeline(app, 
                                    "AndroidBuildPipeline",
                                    props,
                                    env=TARGET_ENV)

app.synth()
