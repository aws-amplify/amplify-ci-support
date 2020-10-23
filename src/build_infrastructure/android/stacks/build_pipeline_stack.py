import boto3
import base64
from ruamel import yaml
import json
import os
from typing import cast
from botocore.exceptions import ClientError
from aws_cdk import (
    aws_iam,
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
from amplify_custom_resources import DeviceFarmProject

class AmplifyAndroidCodePipeline(core.Stack):
    CODE_BUILD_AMPLIFY_ACTIONS = [
            "amplify:List*",
            "amplify:Get*",
            "cloudformation:Get*",
            "cloudformation:Describe*"
        ]
    DEVICE_FARM_TEST_RUNNER_ACTIONS = [
            "devicefarm:List*",
            "devicefarm:Get*",
            "devicefarm:ScheduleRun",
            "devicefarm:DeleteRun",
            "devicefarm:StopRun",
            "devicefarm:CreateUpload",
            "devicefarm:UpdateUpload",
            "devicefarm:DeleteUpload"
        ]
    def __init__(self, scope: core.App, id: str, props, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        if 'github_source' not in props:
            raise RuntimeError("Parameter github_source (aws_codepipeline_actions.GitHubSourceAction) is required.")
        
        amplify_android_build_output = aws_codepipeline.Artifact("AmplifyAndroidBuildOutput")
        github_source = cast(aws_codepipeline_actions.GitHubSourceAction, props['github_source'])
        device_farm_project_arn = props['device_farm_project_arn']
        device_farm_project_id = props['device_farm_project_id']
        device_farm_pool_arn = props['device_farm_pool_arn']
        device_farm_project_name = props['device_farm_project_name']

        # df_project = DeviceFarmProject(self, id, project_name=device_farm_project_name)
        # self.device_farm_project_id = props['device_farm_project_id']
        # self.device_farm_device_pool_arn = props['device_farm_device_pool_arn']
        
        pipeline_project = aws_codebuild.PipelineProject(self, 
                                                        "AmplifyAndroidCodeBuildProject", 
                                                        environment=aws_codebuild.BuildEnvironment(build_image=aws_codebuild.LinuxBuildImage.AMAZON_LINUX_2_3, 
                                                                                                    privileged=True,
                                                                                                    compute_type=aws_codebuild.ComputeType.LARGE),
                                                        build_spec=aws_codebuild.BuildSpec.from_source_filename(filename='buildspec.yml'))
        build_exec_policy = aws_iam.ManagedPolicy(self,
            "AmplifyAndroidBuildExecutorPolicy",
            managed_policy_name=f"AmplifyAndroidBuildExecutorPolicy",
            description="Policy used by the CodeBuild role that executes builds.",
            statements=[
                aws_iam.PolicyStatement(actions=self.CODE_BUILD_AMPLIFY_ACTIONS, effect=aws_iam.Effect.ALLOW, resources=["*"]),
            ]
        )

        df_runner_policy = aws_iam.ManagedPolicy(self,
            "AmplifyAndroidDeviceFarmTestRunnerPolicy",
            managed_policy_name=f"AmplifyAndroidDeviceFarmTestRunnerPolicy",
            description="Policy used by the CodePipeline to trigger DeviceFarm test runs.",
            statements=[
                aws_iam.PolicyStatement(actions=self.DEVICE_FARM_TEST_RUNNER_ACTIONS, effect=aws_iam.Effect.ALLOW, resources=["*"]),
            ]
        )
        build_exec_policy.attach_to_role(pipeline_project.role)

        pipeline = aws_codepipeline.Pipeline(self, 
            "Pipeline",
            stages=[
                aws_codepipeline.StageProps(
                    stage_name="Source",
                    actions=[ github_source ]
                ),
                aws_codepipeline.StageProps(
                    stage_name="Build",
                        actions=[
                        aws_codepipeline_actions.CodeBuildAction(
                            action_name='BuildAndAssemble',
                            input=github_source.action_properties.outputs[0],
                            project=pipeline_project,
                            outputs=[amplify_android_build_output]
                        )
                    ]
                )
            ])
        df_runner_policy.attach_to_role(pipeline.role)

        module_names = ['core', 'aws-analytics-pinpoint', 'aws-datastore', 'aws-api', 'aws-storage-s3', 'aws-predictions']
        test_actions = []
        for module_name in module_names:
            test_actions.append(self._build_device_farm_test_action(device_farm_project_arn, device_farm_project_id, device_farm_pool_arn, module_name))

        testing_stage = {
            "Name": "Test",
            "Actions": test_actions
        }
        pipeline_node = pipeline.node.default_child
        pipeline_node.add_property_override("Stages.2", testing_stage)
    
    def _build_device_farm_test_action(self, project_arn: str, project_id: str, device_pool_arn: str, module_name: str):
        return {
            "Name":f"{module_name}-InstrumentedTests",
            "ActionTypeId": {
                "Category": "Test",
                "Owner": "AWS",
                "Provider": "DeviceFarm",
                "Version": "1"
            },
            "RunOrder": 1,
            "Configuration": {
                "App": f"{module_name}-debug-androidTest.apk",
                "Test": f"{module_name}-debug-androidTest.apk",
                "AppType": "Android",
                "DevicePoolArn": device_pool_arn,
                "ProjectId": project_id,
                "TestType": "INSTRUMENTATION"
            },
            "OutputArtifacts": [],
            "InputArtifacts": [
                {
                    "Name": "AmplifyAndroidBuildOutput"
                }
            ]
            # "Region": "us-west-2"
        }
