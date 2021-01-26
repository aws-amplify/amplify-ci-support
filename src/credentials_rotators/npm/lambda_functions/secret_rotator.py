import logging
import os

import boto3

from secrets_config_utils import get_secrets_config


class SecretRotator:
    """
    Holds the attributes and methods common to any secret rotator lambda
    Attributes:
        arn: The secret ARN or identifier
        token: The ClientRequestToken of the secret version
        Step: The rotation step (one of createSecret, setSecret, testSecret, or finishSecret)
    """

    def __init__(self, arn, token, step):
        self.arn = arn
        self.token = token
        self.step = step
        self.secrets_config = get_secrets_config()

        # Create a Secrets Manager client to be used to access the secret
        # Default to us-west-2 in case region is not specified using AWS_DEFAULT_REGION variable
        session = boto3.session.Session()
        self.service_client = session.client(
            service_name='secretsmanager',
            region_name=os.getenv('AWS_DEFAULT_REGION', 'us-west-2')
        )

        # Re-use the logger instance when possible
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)

    def rotate(self):
        """
        Raises:
            ResourceNotFoundException: If the secret with the specified arn and stage does not exist
            ValueError: If the secret is not properly configured for rotation
            KeyError: If the event parameters do not contain the expected keys
        """
        self.check_secret_versions()

        ## process the current rotation step
        if self.step == "createSecret":
            self.create_secret()
        elif self.step == "setSecret":
            self.set_secret()
        elif self.step == "testSecret":
            self.test_secret()
        elif self.step == "finishSecret":
            self.finish_secret()
        else:
            # should not be any other value unless there is an API change
            # https://docs.aws.amazon.com/secretsmanager/latest/userguide/rotating-secrets-lambda-function-overview.html
            raise ValueError("Invalid step parameter")

    def check_secret_versions(self):
        """Make sure the version is staged correctly
        Raises:
            ValueError: If the secret with the specified token is incorrectly versioned
        """
        metadata = self.service_client.describe_secret(SecretId=self.arn)
        if not metadata['RotationEnabled']:
            self.logger.error("Secret %s is not enabled for rotation" % self.arn)
            raise ValueError("Secret %s is not enabled for rotation" % self.arn)
        versions = metadata['VersionIdsToStages']
        print(f'versions: {versions}')
        if self.token not in versions:
            self.logger.error("Secret version %s has no stage for rotation of secret %s." % (self.token, self.arn))
            raise ValueError("Secret version %s has no stage for rotation of secret %s." % (self.token, self.arn))
        if "AWSCURRENT" in versions[self.token]:
            self.logger.info("Secret version %s already set as AWSCURRENT for secret %s." % (self.token, self.arn))
            return
        elif "AWSPENDING" not in versions[self.token]:
            self.logger.error("Secret version %s not set as AWSPENDING for rotation of secret %s." % (self.token, self.arn))
            raise ValueError("Secret version %s not set as AWSPENDING for rotation of secret %s." % (self.token, self.arn))


    def check_secret_exists(self):
        """Check Existence
        This method checks if the secret to be rotated actually exists by fetching it's current version
        """
        self.service_client.get_secret_value(SecretId=self.arn, VersionStage="AWSCURRENT")


    def create_secret(self):
        """Create the secret
        This method first checks for the existence of a secret for the passed in token. If one does not exist, it will generate a
        new secret and put it with the passed in token.
        Raises:
            NotImplementedError: This method should be implemented by the child classes
        """
        raise NotImplementedError('This method should be implemented by the child classes')


    def set_secret(self):
        """Set the secret
        This method should set the AWSPENDING secret in the service that the secret belongs to.
        Raises:
            NotImplementedError: This method should be implemented by the child classes
        """
        raise NotImplementedError('This method should be implemented by the child classes')


    def test_secret(self):
        """Test the secret
        This method should validate that the AWSPENDING secret works in the service that the secret belongs to.
        Raises:
            NotImplementedError: This method should be implemented by the child classes
        """
        raise NotImplementedError('This method should be implemented by the child classes')


    def finish_secret(self):
        """Finalize the secret rotation
        This method finalizes the rotation process by marking the secret version passed in as the AWSCURRENT secret.
        Raises:
            ResourceNotFoundException: If the secret with the specified arn does not exist
        """
        # First describe the secret to get the current version
        metadata = self.service_client.describe_secret(SecretId=self.arn)
        current_version = None
        for version in metadata["VersionIdsToStages"]:
            if "AWSCURRENT" in metadata["VersionIdsToStages"][version]:
                if version == self.token:
                    # The correct version is already marked as current, return
                    self.logger.info("finishSecret: Version %s already marked as AWSCURRENT for %s" % (version, self.arn))
                    return
                current_version = version
                break

        # Finalize by staging the secret version current
        self.service_client.update_secret_version_stage(SecretId=self.arn,
                                                        VersionStage="AWSCURRENT",
                                                        MoveToVersionId=self.token,
                                                        RemoveFromVersionId=current_version)
        self.logger.info("finishSecret: Successfully set AWSCURRENT stage to version %s for secret %s." % (self.token, self.arn))
