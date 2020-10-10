import boto3
import base64
import os
from typing import cast
from botocore.exceptions import ClientError
from aws_cdk import (
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

class AmplifyAndroidCodePipeline(core.Stack):
    def __init__(self, scope: core.App, id: str, props, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        if 'github_source' not in props:
            raise "Parameter github_source (aws_codepipeline_actions.GitHubSourceAction) is required."

        amplify_android_build_output = aws_codepipeline.Artifact("AmplifyAndroidBuildOutput")
        github_source = cast(aws_codepipeline_actions.GitHubSourceAction, props['github_source'])

        self.add_device_farm_handler_lambda({ 'ProjectName': 'amplify-android - Instrumented Tests'})


        pipeline_project = aws_codebuild.PipelineProject(self, 
                                                        "AmplifyAndroidCodeBuildProject", 
                                                        environment=aws_codebuild.BuildEnvironment(build_image=aws_codebuild.LinuxBuildImage.AMAZON_LINUX_2_3, 
                                                                                                    privileged=True,
                                                                                                    compute_type=aws_codebuild.ComputeType.MEDIUM),
                                                        build_spec=aws_codebuild.BuildSpec.from_source_filename(filename='buildspec.yml'))
        aws_codepipeline.Pipeline(self, 
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
                            action_name='GradleBuild',
                            input=github_source.action_properties.outputs[0],
                            project=pipeline_project,
                            outputs=[amplify_android_build_output]
                        )
                    ]
                )
            ])

    def add_device_farm_handler_lambda(self, props):
        lambda_code = None
        with open(f"{os.getcwd()}/lambdas/device_farm_project_cfn_resource_handler.py", encoding="utf8") as fp:
            lambda_code = fp.read()
        cfn_handler_function = aws_lambda.Function(self, 
            'DeviceFarmProjectCfnHandler',
            code=aws_lambda.InlineCode(code=lambda_code),
            handler='index.handler',
            runtime=aws_lambda.Runtime.PYTHON_3_7
        )
        cfn_lambda_provider = custom_resources.Provider(self, "DeviceFarmProjectCfnHandlerProvider", on_event_handler=cfn_handler_function,log_retention= aws_logs.RetentionDays.ONE_DAY)
        
        core.CustomResource(self, "DeviceFarmProject", service_token=cfn_lambda_provider.service_token, properties=props)