from aws_cdk import core
from aws_cdk.aws_lambda import LayerVersion, Code
from aws_cdk.aws_iam import ServicePrincipal, PolicyStatement, Effect
from aws_cdk.aws_secretsmanager import Secret
from aws_cdk.aws_sns import Topic
from aws_cdk.aws_sns_subscriptions import EmailSubscription
from aws_cdk.aws_cloudwatch_actions import SnsAction
from lambda_functions.secrets_config_utils import get_secrets_config, get_alarm_subscriptions, get_secret_arn, get_secret_key
import subprocess
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class CommonStack(core.Stack):
    """
    Holds the resources and methods common to all rotator stacks
    """

    def __init__(self, scope: core.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        self.dependencies_lambda_layer = self.create_dependencies_layer()
        self.secrets_config = get_secrets_config()

    def create_dependencies_layer(self) -> LayerVersion:
        """
        Creates a lambda layer containing the external packages (pyotp, requests) which are
        required for the secret rotation
        """
        requirements_file = 'lambda_layers/external_dependencies/requirements.txt'
        output_dir = 'lambda_layers/external_dependencies'

        subprocess.check_call(
            f'pip3 install --upgrade -r {requirements_file} -t {output_dir}/python'.split()
        )

        layer_id = 'external-dependencies'
        layer_code = Code.from_asset(output_dir)

        return LayerVersion(self, layer_id, code=layer_code)

    # def get_secrets_config(self):
    #     """Reads the secrets_config.json into a Dictionary
    #     Returns:
    #         The secrets_config.json file as a Dictionary
    #     Raises:
    #         IOError: If the secrets configuration file cannot be read
    #     """
    #     with open('lambda_functions/secrets_config.json') as config_file:
    #         config = json.load(config_file)
    #         return config
    #
    # def get_secret_arn(self, secret_config):
    #     """Gets the full arn of the secret from its configuration
    #     Args:
    #         secret_config (Dictionary): The configuration for the secret specified in secrets_config.json
    #     Returns:
    #         The full arn of the secret as a String
    #     Raises:
    #         KeyError: If the arn is not present in secret configuration
    #     """
    #     try:
    #         return secret_config['arn']
    #     except KeyError as e:
    #         logger.info(f'Invalid config object. Could not read arn from secret configuration: {secret_config}')
    #         raise e
    #
    # def get_secret_key(self, secret_config):
    #     """Gets the key of the secret from its configuration
    #     Args:
    #         secret_config (Dictionary): The configuration for the secret specified in secrets_config.json
    #     Returns:
    #         The key of the secret as a String
    #     Raises:
    #         KeyError: If the key is not present in secret configuration
    #     """
    #     try:
    #         return secret_config['secret_key']
    #     except KeyError as e:
    #         logger.info(f'Invalid config object. Could not read secret_key from secret configuration: {secret_config}')
    #         raise e


    def grant_secrets_manager_access_to_lambda(self, rotator_lambda):
        """
        Adds a resource based policy to the lambda used for rotation
        which gives secrets manager service access to invoke the lambda.
        Documentation can be found here: https://docs.aws.amazon.com/secretsmanager/latest/userguide/troubleshoot_rotation.html#tshoot-lambda-initialconfig-perms
        Args:
            rotator_lambda (Function): The lambda function used for rotating a secret
        """
        service_principal = ServicePrincipal(service='secretsmanager.amazonaws.com')
        rotator_lambda.add_permission('invoke_access_to_secrets_manager', principal=service_principal)

    def grant_lambda_access_to_rotation_secret(self, rotator_lambda, secret_config):
        """
        Adds a custom policy to the lambda role which gives it access to the secret being rotated.
        Documentation can be found here: https://docs.aws.amazon.com/secretsmanager/latest/userguide/troubleshoot_rotation.html#tshoot-lambda-accessdeniedduringrotation
        Args:
            rotator_lambda (Function): The lambda function used for rotating a secret
            secret_config (Dictionary): The configuration for the secret specified in secrets_config.json
        """
        secret_arn = get_secret_arn(secret_config)
        rotator_lambda.add_to_role_policy(PolicyStatement(effect=Effect.ALLOW,
                                                          resources=[secret_arn],
                                                          actions=["secretsmanager:DescribeSecret",
                                                                   "secretsmanager:GetSecretValue",
                                                                   "secretsmanager:PutSecretValue",
                                                                   "secretsmanager:UpdateSecretVersionStage"]
                                                          )
                                          )
        rotator_lambda.add_to_role_policy(PolicyStatement(effect=Effect.ALLOW,
                                                          resources=['*'],
                                                          actions=["secretsmanager:GetRandomPassword"]
                                                          )
                                          )

    def grant_lambda_access_to_secrets(self, rotator_lambda, secret_configs):
        """
        Adds a custom policy to the lambda role which gives it access to the static secrets
        used for authentication.
        Args:
            rotator_lambda (Function): The lambda function used for rotating a secret
            secret_configs (Dictionary): list of configurations for static secrets used for authentication by rotator_lambda
        """
        for secret_config in secret_configs:
            secret_arn = get_secret_arn(secret_config)
            rotator_lambda.add_to_role_policy(PolicyStatement(effect=Effect.ALLOW,
                                                              resources=[secret_arn],
                                                              actions=["secretsmanager:GetSecretValue"]
                                                              )
                                              )

    def configure_secret_rotation(self, rotator_lambda, secret_config, duration):
        """
        Adds the rotator_lambda to the secret referenced using secret_id in the secrets_config.json.
        Args:
            rotator_lambda (Function): The lambda function used for rotating a secret
            secret_config (Dictionary): The configuration for the secret specified in secrets_config.json
            duration (Duration): The rotation time interval
        """
        secret_arn = get_secret_arn(secret_config)
        secret_key = get_secret_key(secret_config)
        secret = Secret.from_secret_complete_arn(self,
                                                 secret_key,
                                                 secret_complete_arn=secret_arn)
        secret.add_rotation_schedule(id=f'{secret_key}-rotator',
                                     automatically_after=duration,
                                     rotation_lambda=rotator_lambda)

    def enable_cloudwatch_alarm_notifications(self, rotator_lambda, secret_id):
        """
        Adds a cloudwatch alarm to monitor the error metrics.
        Subscribes the given emails to receive email alerts.
        Args:
            rotator_lambda (Function): The lambda function used for rotating a secret
            secret_id (string): The identifier corresponding to the secret in the secrets_config.json file
        """
        # create an sns topic for the rotator lambda monitoring
        alarm_sns_topic_id = f'{secret_id}_alarm_sns_topic'
        alarm_sns_topic = Topic(self,
                                alarm_sns_topic_id)

        # subscribe the given emails to the sns topic
        subscription_emails = get_alarm_subscriptions(secret_id)
        for email in subscription_emails:
            alarm_sns_topic.add_subscription(EmailSubscription(email))

        # add errors metric alarm to rotator lambda
        # should send and email notification if the errors metric >= threshold every single time(evaluation_periods)
        errors_alarm_id = f'{secret_id}_errors_alarm'
        errors_alarm = rotator_lambda.metric_errors().create_alarm(self,
                                                                   errors_alarm_id,
                                                                   threshold=1,
                                                                   evaluation_periods=1)
        errors_alarm.add_alarm_action(SnsAction(alarm_sns_topic))
