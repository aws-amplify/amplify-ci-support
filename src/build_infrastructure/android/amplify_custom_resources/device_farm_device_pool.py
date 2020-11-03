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

class DeviceFarmDevicePool(core.Construct):
    DEVICE_FARM_CFN_HANDLER_ACTIONS = [
        "devicefarm:CreateDevicePool",
        "devicefarm:UpdateDevicePool",
        "devicefarm:DeleteDevicePool"
    ]
    device_pool_name = None
    device_pool_arn = None
    custom_resource = None
    def __init__(self, scope: core.Construct, id: str, 
                        project_arn: str,
                        device_pool_name: str, 
                        manufacturer:str = 'Google',
                        platform: str = 'ANDROID',
                        os_version = '10',
                        max_devices=1, 
                        log_retention=None) -> None:
        super().__init__(scope, id)
        self.device_pool_name = device_pool_name
        policy = AwsCustomResourcePolicy.from_sdk_calls(resources=AwsCustomResourcePolicy.ANY_RESOURCE)

        self.custom_resource = AwsCustomResource(scope=self,
            id=f'{id}-CustomResource',
            policy=policy,
            log_retention=log_retention,
            on_create=self.create_device_pool(project_arn, device_pool_name, platform, max_devices, os_version, manufacturer), 
            on_update=self.update_device_pool(device_pool_name, platform, max_devices, os_version, manufacturer), 
            on_delete=self.delete_device_pool(),
            resource_type='Custom::AWS-DeviceFarm-DevicePool')
        self.device_pool_arn = self.custom_resource.get_response_field_reference('devicePool.arn')

    def create_device_pool(self, project_arn, device_pool_name, platform, max_devices, os_version, manufacturer):
        return AwsSdkCall(
            action='createDevicePool',
            service='DeviceFarm',
            parameters={ 'name': device_pool_name, 'projectArn': project_arn, 'rules': self._build_rules(platform, os_version, manufacturer), 'maxDevices': max_devices },
            region='us-west-2', # When other endpoints become available for DF, we won't have to do this.
            physical_resource_id=PhysicalResourceId.from_response("devicePool.arn")
        )

    def update_device_pool(self, device_pool_name, platform, max_devices, os_version, manufacturer):
        return AwsSdkCall(
            action='updateDevicePool',
            service='DeviceFarm',
            parameters={ 'arn': self.device_pool_arn , 'name': device_pool_name, 'rules': self._build_rules(platform, os_version, manufacturer), 'maxDevices': max_devices },
            region='us-west-2', # When other endpoints become available for DF, we won't have to do this.
            physical_resource_id=PhysicalResourceId.from_response("devicePool.arn")
        )

    def delete_device_pool(self):
        return AwsSdkCall(
            action='deleteDevicePool',
            service='DeviceFarm',
            parameters={ 'arn': self.device_pool_arn },
            region='us-west-2', # When other endpoints become available for DF, we won't have to do this.
            physical_resource_id=PhysicalResourceId.from_response("devicePool.arn")
        )

    def _build_rules(self, platform, os_version, manufacturer, availability='HIGHLY_AVAILABLE'):
        return [
            {
                'attribute': 'AVAILABILITY',
                'operator': 'EQUALS',
                'value': f"\"{availability}\""
            },
            {
                'attribute': 'MANUFACTURER',
                'operator': 'EQUALS',
                'value': f"\"{manufacturer}\""
            },
            {
                'attribute': 'PLATFORM',
                'operator': 'EQUALS',
                'value': f"\"{platform}\""
            },
            {
                'attribute': 'OS_VERSION',
                'operator': 'EQUALS',
                'value': f"\"{os_version}\""
            }
        ]
