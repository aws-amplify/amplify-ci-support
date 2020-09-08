from aws_cdk import (
    aws_codebuild,
    aws_codepipeline,
    aws_codepipeline_actions,
    aws_ssm,
    core,
)

class BuildPipelineStack(core.Stack):
    def __init__(self, scope: core.App, id: str, props, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        source_output = aws_codepipeline.Artifact("SourceOutput")
        amplify_android_build_output = aws_codepipeline.Artifact("AmplifyAndroidBuildOutput")

        pipeline_project = aws_codebuild.PipelineProject(self, 
                                                        "AmplifyAndroidCodeBuildProject", 
                                                        environment=aws_codebuild.BuildEnvironment(build_image=aws_codebuild.LinuxBuildImage.AMAZON_LINUX_2_3, privileged=True),
                                                        build_spec=aws_codebuild.BuildSpec.from_source_filename(filename='buildspec.yml'))

        aws_codepipeline.Pipeline(self, 
            "Pipeline",
            stages=[
                aws_codepipeline.StageProps(
                    stage_name="Source",
                    actions=[
                        aws_codepipeline_actions.GitHubSourceAction(
                            output=source_output, 
                            action_name="AmplifySource", 
                            owner="aws-amplify", 
                            repo="amplify-android",
                            branch="main", 
                            oauth_token=core.SecretValue("")
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
                            outputs=[amplify_android_build_output],
                            run_order=1
                        )
                    ]
                )
            ])