import boto3
import base64
from botocore.exceptions import ClientError
from aws_cdk import (
    aws_codebuild,
    aws_codepipeline,
    aws_codepipeline_actions,
    aws_ssm,
    core,
)

class BuildPipelineStack(core.Stack):
    DEFAULT_GITHUB_SECRET_NAME = "AmplifyAndroidSecret"
    DEFAULT_GITHUB_OWNER = "aws-amplify"
    DEFAULT_BRANCH = "main"
    def __init__(self, scope: core.App, id: str, props, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        source_output = aws_codepipeline.Artifact("SourceOutput")
        amplify_android_build_output = aws_codepipeline.Artifact("AmplifyAndroidBuildOutput")

        pipeline_project = aws_codebuild.PipelineProject(self, 
                                                        "AmplifyAndroidCodeBuildProject", 
                                                        environment=aws_codebuild.BuildEnvironment(build_image=aws_codebuild.LinuxBuildImage.AMAZON_LINUX_2_3, 
                                                                                                    privileged=True,
                                                                                                    compute_type=aws_codebuild.ComputeType.MEDIUM),
                                                        build_spec=aws_codebuild.BuildSpec.from_source_filename(filename='buildspec.yml'))
        github_secret_name = self.DEFAULT_GITHUB_SECRET_NAME if 'github_secret_name' not in props else props['github_secret_name']
        github_owner  = self.DEFAULT_GITHUB_OWNER if 'github_owner' not in props else props['github_owner']
        branch  = self.DEFAULT_GITHUB_OWNER if 'branch' not in props else props['branch']
        aws_codepipeline.Pipeline(self, 
            "Pipeline",
            stages=[
                aws_codepipeline.StageProps(
                    stage_name="Source",
                    actions=[
                        aws_codepipeline_actions.GitHubSourceAction(
                            output=source_output, 
                            action_name="AmplifySource", 
                            owner=github_owner, 
                            repo="amplify-android",
                            branch=branch, 
                            oauth_token= core.SecretValue('{{'+f"resolve:secretsmanager:{github_secret_name}:SecretString:token"+'}}')
                        )
                    ]
                ),
                aws_codepipeline.StageProps(
                    stage_name="Build",
                        actions=[
                        aws_codepipeline_actions.CodeBuildAction(
                            action_name='GradleBuild',
                            input=source_output,
                            project=pipeline_project,
                            outputs=[amplify_android_build_output]
                        )
                    ]
                )
            ])