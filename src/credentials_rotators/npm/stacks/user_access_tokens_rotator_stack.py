from aws_cdk import core
from aws_cdk.aws_lambda import *
from stacks.common_stack import CommonStack


class UserAccessTokensRotatorStack(CommonStack):
    """
    Holds the resources necessary for rotating the NPM user's access tokens as specified in `secrets_config.json`
    """
    def __init__(self, scope: core.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        self.secret_id = 'npm_access_token_secrets'

        # TODO: implement
