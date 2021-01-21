import logging
import os
import json
from secrets_manager_utils import get_secret_key, get_secret_value
from secret_rotator import SecretRotator
from npm_utils import update_login_password, get_user_info

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class UserLoginPasswordRotator(SecretRotator):
    """
    Handles the rotation logic specific to rotating the NPM user login password secret
    """

    def __init__(self, arn, token, step):
        super().__init__(arn, token, step)

    def create_secret(self):
        """Create the secret
        This method first checks for the existence of a secret for the passed in token. If one does not exist, it will generate a
        new password for the NPM user and put it with the passed in token.
        Raises:
            ResourceNotFoundException: If the secret with the specified arn and stage does not exist
        """
        # Make sure the current secret exists
        self.check_secret_exists()

        # Now try to get the secret version, if that fails, put a new secret
        try:
            self.service_client.get_secret_value(SecretId=self.arn, VersionId=self.token, VersionStage="AWSPENDING")
            logger.info("createSecret: Successfully retrieved secret for %s." % self.arn)
        except self.service_client.exceptions.ResourceNotFoundException:
            # Get exclude characters from environment variable used to create new password
            exclude_characters = os.environ[
                'EXCLUDE_CHARACTERS'] if 'EXCLUDE_CHARACTERS' in os.environ else '/@"\'\\'
            # Generate a random password
            new_password = self.service_client.get_random_password(ExcludeCharacters=exclude_characters)[
                'RandomPassword']
            npm_login_password_secret_key = get_secret_key('npm_login_password_secret')
            npm_login_password_secret = json.dumps({npm_login_password_secret_key: new_password})

            # Put the secret
            self.service_client.put_secret_value(SecretId=self.arn,
                                                 ClientRequestToken=self.token,
                                                 SecretString=npm_login_password_secret,
                                                 VersionStages=['AWSPENDING'])
            logger.info("createSecret: Successfully put secret for ARN %s and version %s." % (self.arn, self.token))

    def set_secret(self):
        """Set the secret
        This method should set the AWSPENDING secret in as the updated login password for the NPM user
        Raises:
            HttpError: If the API call to update user login password fails
        """
        npm_login_username = get_secret_value(self.service_client, 'npm_login_username_secret')
        print(npm_login_username)

        otp_seed = get_secret_value(self.service_client, 'npm_otp_seed_secret')
        print(f'otp_seed: {otp_seed}')

        current_npm_login_password = get_secret_value(self.service_client, 'npm_login_password_secret')

        new_npm_login_password = get_secret_value(self.service_client, 'npm_login_password_secret', 'AWSPENDING',
                                                  token=self.token)

        print(
            f'user: {npm_login_username} and old pass: {current_npm_login_password} and new pass: {new_npm_login_password}')
        update_login_password(npm_login_username, otp_seed, current_npm_login_password, 'FantaFree@08')

    def test_secret(self):
        """Test the secret
        This method should validate that the pending new password secret works for the NPM user
        Raises:
            HttpError: If the API call to fetch user profile information fails
        """
        npm_login_username = get_secret_value(self.service_client, 'npm_login_username_secret')
        print(npm_login_username)

        otp_seed = get_secret_value(self.service_client, 'npm_otp_seed_secret')
        print(f'otp_seed: {otp_seed}')

        npm_login_password = get_secret_value(self.service_client, 'npm_login_password_secret', 'AWSPENDING',
                                              token=self.token)

        print(f'user: {npm_login_username} and pass: {npm_login_password}')
        get_user_info(npm_login_username, otp_seed, 'FantaFree@08')
