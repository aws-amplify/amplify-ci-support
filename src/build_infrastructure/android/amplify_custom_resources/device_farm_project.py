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

        self.custom_resource = AwsCustomResource(scope=self,
            id=f'{id}-CustomResource',
            policy=policy,
            log_retention=log_retention,
            on_create=self.create_project(project_name), 
            on_update=self.update_project(project_name), 
            on_delete=self.delete_project(project_name),
            resource_type='Custom::AWS-DeviceFarm-Project')
        self.project_arn = self.custom_resource.get_response_field_reference('project.arn')
        self.project_id  = core.Fn.select(6, core.Fn.split(":", core.Token.as_string(self.project_arn)))

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
