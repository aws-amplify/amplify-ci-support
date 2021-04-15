from aws_cdk import (
    core,
    aws_iam
)

from amplify_custom_resources import MavenPublisher

class MavenReleaseStack(core.Stack):
    def __init__(self, scope: core.App, id: str, props, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        required_props = ['github_source']
        for prop in required_props:
            if prop not in props:
                raise RuntimeError(f"Parameter {prop} is required.")
        
        codebuild_project_name_prefix = props['codebuild_project_name_prefix']

        github_source = props['github_source']
        owner = github_source['owner']
        repo = github_source['repo']
        base_branch = github_source['base_branch']
        buildspec_path = props['buildspec_path'] if 'buildspec_path' in props else "scripts/maven-release-publisher.yml"
        create_webhooks = props['create_webhooks']

        policy = aws_iam.ManagedPolicy(self,    
                "SecretsAccessPolicy", 
                managed_policy_name=f"{codebuild_project_name_prefix}-SecretsAccessPolicy",
                description="Policy used by the CodeBuild role to access secrets when uploading to Sonatype",
                statements=[
                    aws_iam.PolicyStatement(
                        actions=["secretsmanager:GetSecretValue"], 
                        effect=aws_iam.Effect.ALLOW, 
                        resources=[
                            f"arn:aws:secretsmanager:{self.region}:{self.account}:secret:awsmobilesdk/android/signing*",
                            f"arn:aws:secretsmanager:{self.region}:{self.account}:secret:awsmobilesdk/android/sonatype*"
                        ]
                    )
                ]
            )

        publisher = MavenPublisher(self, "ReleasePublisher", project_name=f"{codebuild_project_name_prefix}-ReleasePublisher",
                                                   github_owner=owner, 
                                                   github_repo=repo, 
                                                   base_branch=base_branch,
                                                   buildspec_path=buildspec_path,
                                                   create_webhooks=create_webhooks)
        
        policy.attach_to_role(publisher.role)