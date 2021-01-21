#!/usr/bin/env python3

from aws_cdk import core
from stacks.user_login_password_rotator_stack import UserLoginPasswordRotatorStack
from stacks.user_access_tokens_rotator_stack import UserAccessTokensRotatorStack


app = core.App()

# Stack with necessary infrastructure to rotate npm login password secret
UserLoginPasswordRotatorStack(app, "UserLoginPasswordRotatorStack")

# Stack with necessary infrastructure to rotate npm user's access tokens specified in `secrets_config.json`
UserAccessTokensRotatorStack(app, "UserAccessTokensRotatorStack")

app.synth()
