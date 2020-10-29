from aws_cdk import (
    aws_codebuild,
    aws_codepipeline,
    aws_codepipeline_actions,
    aws_ssm,
    core,
)

class AmplifyAndroidRepoConnection(aws_codepipeline_actions.BitBucketSourceAction):
    """
    Even though we're using BitBucketSourceAction, this works for any type of CodeStar connection 
    according to this post in the CDK repo. (https://github.com/aws/aws-cdk/issues/10632)
    """
    REPO_NAME = 'amplify-android'
    BRANCH = 'main'
    OWNER = 'aws-amplify'
    TRIGGER = aws_codepipeline_actions.GitHubTrigger.NONE
    SECRET_NAME = "AmplifyAndroidSecret"
    SOURCE_OUTPUT_NAME = "AmplifyAndroidSource"
    ACTION_NAME = "AmplifyAndroidGitHubRepo"
    def __init__(self, 
                    connection_arn: str,
                    owner_override:str = None, 
                    branch_override: str = None,
                    source_output_name_override: str = None
                ) -> None:
        source_output_name = self.SOURCE_OUTPUT_NAME if source_output_name_override is None else source_output_name_override
        self.owner = self.OWNER if owner_override is None else owner_override
        self.repo = self.REPO_NAME
        super().__init__(owner = self.owner, 
            repo = self.REPO_NAME,
            connection_arn=connection_arn,
            output = aws_codepipeline.Artifact(source_output_name), 
            variables_namespace=f"{self.ACTION_NAME}Variables",
            action_name = self.ACTION_NAME,
            code_build_clone_output=True,
            branch = self.BRANCH if branch_override is None else branch_override)
