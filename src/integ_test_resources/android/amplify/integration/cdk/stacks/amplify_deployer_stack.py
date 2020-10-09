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

        build_file_path = 'src/integ_test_resources/android/amplify/integration/cdk/scripts/buildspec.yml'
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
        individual_actions = [
            "amplify:Get*",
            "amplify:List*",
            "iam:CreateRole",
            "iam:DeleteRole",
            "iam:CreatePolicy",
            "iam:DeletePolicy",
            "iam:PutRolePolicy",
            "iam:DeleteRolePolicy",
            "iam:CreatePolicyVersion",
            "iam:DeletePolicyVersion",
            "iam:AttachRolePolicy",
            "iam:DetachRolePolicy",
            "cognito-identity:DescribeIdentityPool"
        ]

        policy = aws_iam.ManagedPolicy(self,
            "AmplifyCodeBuildScriptRunnerPolicy",
            managed_policy_name="AmplifyCodeBuildScriptRunnerPolicy",
            description="Policy used by the CodeBuild role that manages the creation of backend resources using the Amplify CLI",
            # document=aws_iam.PolicyDocument(
            statements=[
                aws_iam.PolicyStatement(actions=individual_actions, effect=aws_iam.Effect.ALLOW, resources=["*"]),
            ]
            # )

        )

        policy.attach_to_role(project.role)

        project.role.add_managed_policy(aws_iam.ManagedPolicy.from_aws_managed_policy_name("AmazonS3FullAccess"))
        project.role.add_managed_policy(aws_iam.ManagedPolicy.from_aws_managed_policy_name("AWSCloudFormationFullAccess"))
        project.role.add_managed_policy(aws_iam.ManagedPolicy.from_aws_managed_policy_name('IAMReadOnlyAccess'))
        project.role.add_managed_policy(aws_iam.ManagedPolicy.from_aws_managed_policy_name('AWSLambdaFullAccess'))
        project.role.add_managed_policy(aws_iam.ManagedPolicy.from_aws_managed_policy_name('AWSAppSyncAdministrator'))
