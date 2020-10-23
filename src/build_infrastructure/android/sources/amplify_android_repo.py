from aws_cdk import (
    aws_codebuild,
    aws_codepipeline,
    aws_codepipeline_actions,
    aws_ssm,
    core,
)

class AmplifyAndroidRepo(aws_codepipeline_actions.GitHubSourceAction):
    REPO_NAME = 'amplify-android'
    BRANCH = 'main'
    OWNER = 'aws-amplify'
    TRIGGER = aws_codepipeline_actions.GitHubTrigger.NONE
    SECRET_NAME = "AmplifyAndroidSecret"
    SOURCE_OUTPUT_NAME = "AmplifyAndroidSource"
    ACTION_NAME = "AmplifyAndroidGitHubRepo"
    def __init__(self, 
                    owner_override:str = None, 
                    branch_override: str = None,
                    oauth_token_secret_name_override: str = None,
                    trigger_override: aws_codepipeline_actions.GitHubTrigger = None,
                    source_output_name_override: str = None
                ) -> None:
        source_output_name = self.SOURCE_OUTPUT_NAME if source_output_name_override is None else source_output_name_override
        oauth_token_secret_name = self.SECRET_NAME if oauth_token_secret_name_override is None else oauth_token_secret_name_override
        
        super().__init__(owner = self.OWNER if owner_override is None else owner_override, 
            repo = self.REPO_NAME, 
            output = aws_codepipeline.Artifact(source_output_name), 
            action_name = self.ACTION_NAME,
            branch = self.BRANCH if branch_override is None else branch_override,
            trigger = self.TRIGGER if trigger_override is None else trigger_override,
            oauth_token = core.SecretValue('{{'+f"resolve:secretsmanager:{oauth_token_secret_name}:SecretString:token"+'}}'))

