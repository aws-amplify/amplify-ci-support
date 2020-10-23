import boto3
import os
from typing import cast
from botocore.exceptions import ClientError

from aws_cdk import (
    aws_iam,
    aws_cloudformation,
    aws_logs,
    custom_resources,
    aws_lambda,
    core,
)
from amplify_custom_resources import DeviceFarmProject

class DeviceFarmBootstrap(core.Stack):
    DEVICE_FARM_CFN_HANDLER_ACTIONS = [
            "devicefarm:DeleteProject",
            "devicefarm:CreateProject",
            "devicefarm:UpdateProject"
        ]
    device_farm_cfn_handler_service_token = None
    project_arn_export_name  = None
    df_project = None
    def __init__(self, scope: core.App, id: str, props, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        project_name = props['device_farm_project_name']
        self.project_arn_export_name = f"{id}DeviceFarmProjectArn"
        self.df_project = DeviceFarmProject(self, id, project_name=project_name)
        
        core.CfnOutput(self, self.project_arn_export_name, value=self.df_project.get_arn(), export_name=self.project_arn_export_name)

    def get_device_farm_project_arn(self):
        return core.Fn.import_value(self.project_arn_export_name)