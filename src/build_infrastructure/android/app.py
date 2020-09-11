#!/usr/bin/env python3

import os
from aws_cdk import core
from cdk_build_pipeline.build_pipeline_stack import BuildPipelineStack

app = core.App()
TARGET_REGION = app.node.try_get_context("region")
TARGET_ACCOUNT = app.node.try_get_context("account")
TARGET_ENV=core.Environment( account=TARGET_ACCOUNT, region=TARGET_REGION)

github_owner=app.node.try_get_context("github_owner")
branch=app.node.try_get_context("branch")

print(f"AWS Account={TARGET_ACCOUNT} Region={TARGET_REGION}")

props = {}
if github_owner is not None:
    props['github_owner'] = github_owner
if branch is not None:
    props['branch'] = branch

pipeline_stack = BuildPipelineStack(app, 
                                    "AndroidBuildPipeline",
                                    props,
                                    env=TARGET_ENV)

app.synth()
