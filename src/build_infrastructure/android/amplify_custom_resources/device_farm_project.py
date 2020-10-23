import boto3
import os
from typing import cast
from botocore.exceptions import ClientError

from aws_cdk import (
    aws_iam,
    aws_cloudformation,
    aws_logs,
    aws_lambda,
    core,
)
from aws_cdk.custom_resources import (
    AwsCustomResource, AwsCustomResourcePolicy, AwsSdkCall, PhysicalResourceId
)

class DeviceFarmProject(core.Construct):
    DEVICE_FARM_CFN_HANDLER_ACTIONS = [
        "devicefarm:DeleteProject",
        "devicefarm:CreateProject",
        "devicefarm:UpdateProject"
    ]
    project_name = None
    project_arn = None
    project_id = None
    custom_resource = None
    def __init__(self, scope: core.Construct, id: str, project_name: str, log_retention=None) -> None:
        super().__init__(scope, id)
        self.project_name = project_name
        policy = AwsCustomResourcePolicy.from_sdk_calls(resources=AwsCustomResourcePolicy.ANY_RESOURCE)
        lambda_role = aws_iam.Role(
            scope=self,
            id=f'{id}-LambdaRole',
            assumed_by=aws_iam.ServicePrincipal('lambda.amazonaws.com'),
            managed_policies=[aws_iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole")],
            inline_policies={ 'DeviceFarmProjectPolicy': aws_iam.PolicyDocument(statements=[
                    aws_iam.PolicyStatement(actions=self.DEVICE_FARM_CFN_HANDLER_ACTIONS, effect=aws_iam.Effect.ALLOW, resources=["*"])
                ])
            }
        )

        self.custom_resource = AwsCustomResource(scope=self,
            id=f'{id}-CustomResource',
            policy=policy,
            log_retention=log_retention,
            on_create=self.create_project(project_name), 
            on_update=self.update_project(project_name), 
            on_delete=self.delete_project(project_name),
            resource_type='Custom::AWS-DeviceFarm-Project',
            role=lambda_role)
        project_arn = core.Fn.ref(self.custom_resource.node) # self.custom_resource.get_response_field('project.arn')
        self.project_arn = core.Token.as_string(project_arn)
        self.project_id  = core.Fn.select(6, core.Fn.split(":", self.project_arn))

    def create_project(self, project_name):
        return AwsSdkCall(
            action='createProject',
            service='DeviceFarm',
            parameters={ 'name': project_name },
            region='us-west-2', # When other endpoints become available for DF, we won't have to do this.
            physical_resource_id=PhysicalResourceId.from_response("project.arn")
        )

    def update_project(self, project_name):
        return AwsSdkCall(
            action='updateProject',
            service='DeviceFarm',
            parameters={ 'name': project_name, 'arn': self.project_arn },
            region='us-west-2', # When other endpoints become available for DF, we won't have to do this.
            physical_resource_id=PhysicalResourceId.from_response("project.arn")
        )

    def delete_project(self, project_name):
        return AwsSdkCall(
            action='deleteProject',
            service='DeviceFarm',
            parameters={ 'arn': self.project_arn },
            region='us-west-2', # When other endpoints become available for DF, we won't have to do this.
            physical_resource_id=PhysicalResourceId.from_response("project.arn")
        )

    def get_arn(self):
        return self.project_arn

    def get_project_id(self):
        return self.project_id
        