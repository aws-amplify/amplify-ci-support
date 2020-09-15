import boto3
import os
from typing import cast
from botocore.exceptions import ClientError

from aws_cdk import (
    aws_cloudformation,
    aws_logs,
    custom_resources,
    aws_lambda,
    core,
)

class AccountBootstrap(core.Stack):
    def __init__(self, scope: core.App, id: str, props, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        lambda_code = None
        with open(f"{os.getcwd()}/lambdas/device_farm_project_cfn_resource_handler.py", encoding="utf8") as fp:
            lambda_code = fp.read()
        cfn_handler_function = aws_lambda.Function(self, 
            'DeviceFarmProjectCfnHandler',
            code=aws_lambda.InlineCode(code=lambda_code),
            handler='handler',
            runtime=aws_lambda.Runtime.PYTHON_3_7
        )
        cfn_lambda_provider = custom_resources.Provider(self, "DeviceFarmProjectCfnHandlerProvider", on_event_handler=cfn_handler_function,log_retention= aws_logs.RetentionDays.ONE_DAY)
        
        core.CustomResource(self, "DeviceFarmProject", service_token=cfn_lambda_provider.service_token)