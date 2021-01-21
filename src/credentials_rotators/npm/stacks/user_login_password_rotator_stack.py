from aws_cdk import core
from aws_cdk.aws_lambda import *
from stacks.common_stack import CommonStack


class UserLoginPasswordRotatorStack(CommonStack):
    """
    Holds the resources necessary for NPM user login password rotation
    """
    def __init__(self, scope: core.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        self.secret_id = 'npm_login_password_secret'

        rotator_lambda = Function(
            self,
            'npm_login_password_rotator',
            runtime=Runtime.PYTHON_3_8,
            code=Code.asset('lambda_functions'),
            handler='rotation_handlers.rotate_login_password',
            layers=[
                self.dependencies_lambda_layer
            ]
        )

        required_static_secret_ids = ['npm_login_username_secret', 'npm_otp_seed_secret']
        # Add required permissions
        self.grant_secrets_manager_access_to_lambda(rotator_lambda)
        self.grant_lambda_access_to_rotation_secret(rotator_lambda, self.secret_id)
        self.grant_lambda_access_to_static_secrets(rotator_lambda, required_static_secret_ids)
        self.configure_secret_rotation(rotator_lambda, self.secret_id, core.Duration.days(5))

        # add cloudwatch alarm
        subscription_emails = ['edupp@amazon.com']
        self.enable_cloudwatch_alarm_notifications(self.secret_id, rotator_lambda,subscription_emails)
