from aws_cdk import core
from aws_cdk.aws_lambda import *

from lambda_functions.secrets_config_utils import (
    get_access_token_secrets_configs, get_secret_config)
from stacks.common_stack import CommonStack

class UserAccessTokensRotatorStack(CommonStack):
    """
    Holds the resources necessary for NPM user access tokens rotation
    """
    def __init__(self, scope: core.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        secret_configs = get_access_token_secrets_configs('npm_access_token_secrets')

        rotator_lambda = Function(
            self,
            'npm_access_key_rotator',
            runtime=Runtime.PYTHON_3_8,
            code=Code.asset('lambda_functions'),
            handler='rotation_handlers.rotate_access_keys',
            layers=[
                self.dependencies_lambda_layer
            ]
        )

        # user credentials used for authentication
        required_secret_ids = ['npm_login_username_secret',
                               'npm_otp_seed_secret',
                               'npm_login_password_secret']
        required_secret_configs = [get_secret_config(secret_id) for secret_id in required_secret_ids]

        # Add required permissions
        self.grant_secrets_manager_access_to_lambda(rotator_lambda)
        self.grant_lambda_access_to_secrets(rotator_lambda, required_secret_configs)
        for secret_config in secret_configs:
            self.grant_lambda_access_to_rotation_secret(rotator_lambda, secret_config)
            self.configure_secret_rotation(rotator_lambda, secret_config, core.Duration.days(5))

        # add cloudwatch alarm email notifications
        self.enable_cloudwatch_alarm_notifications(rotator_lambda, 'npm_access_token_secrets')
