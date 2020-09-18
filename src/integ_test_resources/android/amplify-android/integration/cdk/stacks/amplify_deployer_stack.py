import boto3
import base64
from botocore.exceptions import ClientError
from aws_cdk import (
    aws_codebuild,
    aws_iam,
    core,
)

class AmplifyDeployer(core.Stack):
    DEFAULT_GITHUB_OWNER = "aws-amplify"
    DEFAULT_BRANCH = "refs/heads/main"
    def __init__(self, scope: core.App, id: str, props, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        build_file_path = 'src/integ_test_resources/android/amplify-android/integration/cdk/scripts/buildspec.yml'
        github_repo = props['github_repo']
        github_owner  = self.DEFAULT_GITHUB_OWNER if 'github_owner' not in props else props['github_owner']
        branch  = self.DEFAULT_BRANCH if 'branch' not in props else props['branch']
        build_environment = aws_codebuild.BuildEnvironment(build_image=aws_codebuild.LinuxBuildImage.AMAZON_LINUX_2_3, 
                                                            privileged=True,
                                                            compute_type=aws_codebuild.ComputeType.SMALL)
        
        project = aws_codebuild.Project(self,
                                        props['project_name'],
                                        source=aws_codebuild.Source.git_hub(owner=github_owner, 
                                                                            report_build_status=False,
                                                                            repo=github_repo, 
                                                                            branch_or_ref=branch,
                                                                            webhook=False), # Will need to setup creds to make this true
                                        environment=build_environment,
                                        build_spec=aws_codebuild.BuildSpec.from_source_filename(filename=build_file_path))
                                        
        project.role.add_managed_policy(aws_iam.ManagedPolicy.from_aws_managed_policy_name("AmazonS3ReadOnlyAccess"))
        project.role.add_managed_policy(aws_iam.ManagedPolicy.from_aws_managed_policy_name("AWSCloudFormationFullAccess"))

        aws_iam.Policy(
            self,
            "AmplifyDeployerPolicy",
            statements=[
                aws_iam.PolicyStatement(actions=["amplify:*"], effect=aws_iam.Effect.ALLOW, resources=["*"]),
                
            ],
            roles=[
                project.role
            ]
        )
