
import boto3
import base64
from ruamel import yaml
import json
import os
from typing import cast
from botocore.exceptions import ClientError
from aws_cdk import (
    core,
    custom_resources,
    aws_iam,
    aws_codebuild,
    aws_codepipeline,
    aws_codepipeline_actions,
    aws_cloudformation,
    aws_lambda,
    aws_logs,
    aws_s3
)



class PullRequestBuilder(aws_codebuild.Project):
    def __init__(self, scope: core.Construct, id: str, *,
                    project_name: str,
                    github_owner,
                    github_repo,
                    base_branch: str = "main"):

        build_environment = aws_codebuild.BuildEnvironment(build_image=aws_codebuild.LinuxBuildImage.AMAZON_LINUX_2_3, 
                                                            privileged=True,
                                                            compute_type=aws_codebuild.ComputeType.LARGE)
        trigger_on_pr = aws_codebuild.FilterGroup.in_event_of(aws_codebuild.EventAction.PULL_REQUEST_CREATED,
                                                              aws_codebuild.EventAction.PULL_REQUEST_UPDATED).and_base_branch_is(base_branch)
            
        super().__init__(scope, id,
            project_name=project_name,
            build_spec=aws_codebuild.BuildSpec.from_source_filename("scripts/pr-builder-buildspec.yml"),
            source=aws_codebuild.Source.git_hub(owner=github_owner,
                                                report_build_status=True,
                                                repo=github_repo, 
                                                webhook=True,
                                                webhook_filters=[trigger_on_pr]),
            environment=build_environment)
