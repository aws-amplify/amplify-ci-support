import boto3
import base64
from typing import cast
from botocore.exceptions import ClientError
from aws_cdk import (
    aws_codebuild,
    aws_codepipeline,
    aws_codepipeline_actions,
    aws_ssm,
    core,
)

class AmplifyAndroidCodePipeline(core.Stack):
    def __init__(self, scope: core.App, id: str, props, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        if 'github_source' not in props:
            raise "Parameter github_source (aws_codepipeline_actions.GitHubSourceAction) is required."

        amplify_android_build_output = aws_codepipeline.Artifact("AmplifyAndroidBuildOutput")
        github_source = cast(aws_codepipeline_actions.GitHubSourceAction, props['github_source'])

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