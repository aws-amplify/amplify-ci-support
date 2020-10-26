import boto3
import base64
from ruamel import yaml
import json
import os
from botocore.exceptions import ClientError
from aws_cdk import (
    aws_iam,
    aws_sam,
    aws_codebuild,
    aws_codepipeline,
    aws_codepipeline_actions,
    aws_ssm,
    aws_cloudformation,
    aws_logs,
    custom_resources,
    aws_lambda,
    core,
)


class GithubReporting(core.Stack):
    SECRET_NAME = "AmplifyAndroidSecret"
    LOG_LEVEL="INFO"
    def __init__(self, scope: core.App, id: str, props, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        oauth_token_secret_name_override=props['oauth_token_secret_name_override']
        code_build_project_name=props['code_build_project_name']
        oauth_token_secret_name = self.SECRET_NAME if oauth_token_secret_name_override is None else oauth_token_secret_name_override
        log_level = self.LOG_LEVEL if "log_level" not in props else props['log_level']
        
        codebuild_reporting_app = aws_sam.CfnApplication.ApplicationLocationProperty(
            application_id='arn:aws:serverlessrepo:us-east-1:277187709615:applications/github-codebuild-logs',
            semantic_version='1.4.0'
        )
        aws_sam.CfnApplication(self,
            id,
            location=codebuild_reporting_app,
            parameters={
                'CodeBuildProjectName': code_build_project_name,
                'GitHubOAuthToken': core.Token.as_string(core.SecretValue('{{'+f"resolve:secretsmanager:{oauth_token_secret_name}:SecretString:token"+'}}')),
                'DeletePreviousComments': True,
                'LogLevel': log_level
            }
        )