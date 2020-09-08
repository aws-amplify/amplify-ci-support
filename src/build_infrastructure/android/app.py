#!/usr/bin/env python3

from aws_cdk import core
from cdk_build_pipeline.build_pipeline_stack import BuildPipelineStack

app = core.App()

region = app.node.try_get_context("region")
account = app.node.try_get_context("account")
if region is None or account is None:
    raise ValueError(
        "Provide region and account in 'context' parameter, as in: cdk deploy app -c region=us-west-2 -c account=123456"  # noqa: E501
    )

pipeline_stack = BuildPipelineStack(app, 
                                    "AndroidBuildPipeline",
                                    {'pipeline_name':'amplify-android-pipeline', 'codebuild_project_name':'amplify-android-gradle-build'},
                                    env={ 'account': account, 'region': region})
app.synth()
