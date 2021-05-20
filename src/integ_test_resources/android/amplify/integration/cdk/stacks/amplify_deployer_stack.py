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
    DEFAULT_BRANCH = "main"
    SCRIPTS_PATH = "src/integ_test_resources/android/amplify/integration/cdk/scripts"

    def __init__(self, scope: core.App, id: str, props, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        shell_script_name = props['shell_script_name']
        cb_project_name = props['cb_project_name']
        github_repo = props['github_repo']
        github_owner  = self.DEFAULT_GITHUB_OWNER if 'github_owner' not in props else props['github_owner']
        branch  = self.DEFAULT_BRANCH if 'branch' not in props else props['branch']
        build_environment = aws_codebuild.BuildEnvironment(build_image=aws_codebuild.LinuxBuildImage.AMAZON_LINUX_2_3, 
                                                            privileged=True,
                                                            compute_type=aws_codebuild.ComputeType.SMALL)
        
        project = aws_codebuild.Project(self,
                                        cb_project_name,
                                        source=aws_codebuild.Source.git_hub(owner=github_owner, 
                                                                            report_build_status=False,
                                                                            repo=github_repo, 
                                                                            branch_or_ref=branch,
                                                                            webhook=False), # Will need to setup creds to make this true
                                        environment=build_environment,
                                        build_spec=self._generate_buildspec(shell_script_name))
        individual_actions = [
            "amplify:*",
            "cognito-identity:CreateIdentityPool",
            "cognito-identity:DeleteIdentityPool",
            "cognito-identity:DescribeIdentityPool",
            "cognito-identity:ListIdentityPools",
            "cognito-identity:ListTagsForResource",
            "cognito-identity:SetIdentityPoolRoles",
            "cognito-identity:UpdateIdentityPool",
            "cognito-idp:CreateGroup",
            "cognito-idp:CreateIdentityProvider",
            "cognito-idp:CreateResourceServer",
            "cognito-idp:CreateUserPool",
            "cognito-idp:CreateUserPoolClient",
            "cognito-idp:CreateUserPoolDomain",
            "cognito-idp:DeleteGroup",
            "cognito-idp:DeleteIdentityProvider",
            "cognito-idp:DeleteResourceServer",
            "cognito-idp:DeleteUserPool",
            "cognito-idp:DeleteUserPoolClient",
            "cognito-idp:DeleteUserPoolDomain",
            "cognito-idp:DescribeIdentityProvider",
            "cognito-idp:DescribeResourceServer",
            "cognito-idp:DescribeUserPool",
            "cognito-idp:DescribeUserPoolClient",
            "cognito-idp:DescribeUserPoolDomain",
            "cognito-idp:ListGroups",
            "cognito-idp:ListIdentityProviders",
            "cognito-idp:ListResourceServers",
            "cognito-idp:ListTagsForResource",
            "cognito-idp:ListUserImportJobs",
            "cognito-idp:ListUserPoolClients",
            "cognito-idp:ListUserPools",
            "cognito-idp:UpdateGroup",
            "cognito-idp:UpdateIdentityProvider",
            "cognito-idp:UpdateResourceServer",
            "cognito-idp:UpdateUserPool",
            "cognito-idp:UpdateUserPoolClient",
            "cognito-idp:UpdateUserPoolDomain",
            "iam:AttachRolePolicy",
            "iam:CreatePolicy",
            "iam:CreatePolicyVersion",
            "iam:CreateRole",
            "iam:DeletePolicy",
            "iam:DeletePolicyVersion",
            "iam:DeleteRole",
            "iam:DeleteRolePolicy",
            "iam:DetachRolePolicy",
            "iam:PutRolePolicy",
        ]

        policy = aws_iam.ManagedPolicy(self,
            "AmplifyCodeBuildScriptRunnerPolicy",
            managed_policy_name=f"AmplifyCodeBuildScriptRunnerPolicy-{cb_project_name}",
            description="Policy used by the CodeBuild role that manages the creation of backend resources using the Amplify CLI",
            statements=[
                aws_iam.PolicyStatement(actions=individual_actions, effect=aws_iam.Effect.ALLOW, resources=["*"]),
            ]
        )

        policy.attach_to_role(project.role)

        project.role.add_managed_policy(aws_iam.ManagedPolicy.from_aws_managed_policy_name("AmazonS3FullAccess"))
        project.role.add_managed_policy(aws_iam.ManagedPolicy.from_aws_managed_policy_name("AWSCloudFormationFullAccess"))
        project.role.add_managed_policy(aws_iam.ManagedPolicy.from_aws_managed_policy_name('IAMReadOnlyAccess'))
        project.role.add_managed_policy(aws_iam.ManagedPolicy.from_aws_managed_policy_name('AWSLambdaFullAccess'))
        project.role.add_managed_policy(aws_iam.ManagedPolicy.from_aws_managed_policy_name('AWSAppSyncAdministrator'))
    
    def _generate_buildspec(self, shell_script_name: str):
        deployer_command = f"{self.SCRIPTS_PATH}/{shell_script_name}"
        return aws_codebuild.BuildSpec.from_object({
            "version": "0.2",
            "phases": {
                "install": {
                    "commands":[
                        "echo 'Install phase starting'",
                        "npm install -g @aws-amplify/cli@4.40.1"
                    ]
                },
                "build": {
                    "commands": [
                        "echo 'Build phase starting'",
                        deployer_command
                    ]
                }
            }
        })
        
