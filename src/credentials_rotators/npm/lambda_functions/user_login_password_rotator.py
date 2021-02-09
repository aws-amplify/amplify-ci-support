import json
import os

from npm_credentials_rotator import NPMCredentialsRotator
from npm_utils import get_user_info_using_password, update_login_password
from secrets_config_utils import get_secret_config, get_secret_key
from secrets_manager_utils import get_secret_value


class UserLoginPasswordRotator(NPMCredentialsRotator):
    """
    Handles the rotation logic specific to rotating the NPM user login password secret
    """

    def __init__(self, arn, token, step):
        super().__init__(arn, token, step)

    def create_secret(self):
        """Create the secret
        This method first checks for the existence of a secret for the passed in request token. If one does not exist, it will generate a
        new password for the NPM user and put it with the passed in request token.
        Raises:
            ResourceNotFoundException: If the secret with the specified arn and stage does not exist
        """
        # Make sure the current secret exists
        self.check_secret_exists()

        # Now try to get the secret's pending version, if that fails, put a new secret
        try:
            self.service_client.get_secret_value(SecretId=self.arn, VersionId=self.token, VersionStage="AWSPENDING")
            self.logger.warning("createSecret: Successfully retrieved pending secret version")
            return
        except self.service_client.exceptions.ResourceNotFoundException:
            self.logger.info("No pending secret versions exists, creating new secret")

        new_password = self.create_random_password()
        npm_login_password_secret_config = get_secret_config('npm_login_password_secret')
        npm_login_password_secret_key = get_secret_key(npm_login_password_secret_config)
        npm_login_password_secret = json.dumps({npm_login_password_secret_key: new_password})

        # Put the secret
        self.service_client.put_secret_value(SecretId=self.arn,
                                             ClientRequestToken=self.token,
                                             SecretString=npm_login_password_secret,
                                             VersionStages=['AWSPENDING'])
        self.logger.info('createSecret: Successfully put secret')

    def set_secret(self):
        """Set the secret
        This method should set the AWSPENDING secret in as the updated login password for the NPM user
        Raises:
            HttpError: If the API call to update user login password fails
        """
        new_login_password = get_secret_value(self.service_client,
                                              get_secret_config('npm_login_password_secret'),
                                              'AWSPENDING',
                                              token=self.token)

        update_login_password(self.login_username, self.otp_seed, self.login_password, new_login_password)
        self.logger.info('setSecret: Successfully set secret')

    def test_secret(self):
        """Test the secret
        This method should validate that the pending new password secret works for the NPM user
        Raises:
            HttpError: If the API call to fetch user profile information fails
        """
        pending_login_password = get_secret_value(self.service_client,
                                                  get_secret_config('npm_login_password_secret'),
                                                  'AWSPENDING',
                                                  token=self.token)

        get_user_info_using_password(self.login_username, self.otp_seed, pending_login_password)
        self.logger.info('testSecret: Successfully tested secret')

    def create_random_password(self):
        """Creates a random string to be set as password for a NPM user
        """
        # Get exclude characters from environment variable used to create new password
        exclude_characters = os.environ[
            'EXCLUDE_CHARACTERS'] if 'EXCLUDE_CHARACTERS' in os.environ else '/@"\'\\'
        # Generate a random password
        new_password = self.service_client.get_random_password(ExcludeCharacters=exclude_characters)[
            'RandomPassword']
        return new_password
