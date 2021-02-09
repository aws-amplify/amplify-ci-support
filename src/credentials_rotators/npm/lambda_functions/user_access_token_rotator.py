import json

from npm_credentials_rotator import NPMCredentialsRotator
from npm_utils import (create_access_token, delete_access_token, get_user_info_using_access_token)
from secrets_config_utils import (get_access_token_secrets_configs, get_secret_key)
from secrets_manager_utils import get_secret_value


class UserAccessTokenRotator(NPMCredentialsRotator):
    """
    Handles the rotation logic specific to rotating the NPM user login password secret
    """

    def __init__(self, arn, token, step):
        super().__init__(arn, token, step)
        self.secret_config = self.get_access_token_secret_config()

    def create_secret(self):
        """Create the secret
        This method first checks for the existence of a secret for the passed in request token. If one does not exist,
         it will create a new access token for the NPM user and put it with the passed in client request token.
        Raises:
            ResourceNotFoundException: If the secret with the specified arn and stage does not exist
        """
        # Make sure the current secret exists
        self.check_secret_exists()

        # Now try to get the secret version, if that fails, put a new secret
        try:
            self.service_client.get_secret_value(SecretId=self.arn, VersionId=self.token, VersionStage="AWSPENDING")
            self.logger.info("createSecret: Successfully retrieved secret")
        except self.service_client.exceptions.ResourceNotFoundException:
            # create a new access token
            new_access_token = create_access_token(self.login_username, self.otp_seed, self.login_password)

            # Put the secret
            npm_access_token_secret_key = get_secret_key(self.secret_config)
            npm_access_token_secret = json.dumps({npm_access_token_secret_key: new_access_token})
            self.service_client.put_secret_value(SecretId=self.arn,
                                                 ClientRequestToken=self.token,
                                                 SecretString=npm_access_token_secret,
                                                 VersionStages=['AWSPENDING'])
            self.logger.info('createSecret: Successfully put secret')

    def set_secret(self):
        """
        Since, a new access token is already set in the create_secret step, skip this step
        """
        self.logger.info('setSecret: Skip set secret for ARN %s and version %s.' % (self.arn, self.token))
        return

    def test_secret(self):
        """Test the secret
        This method should validate that the pending acess token secret is properly for the NPM user
        Raises:
            HttpError: If the access token is not added to the user account
        """
        # create a new access token
        access_token = get_secret_value(self.service_client,
                                        self.secret_config,
                                        'AWSPENDING',
                                        token=self.token)

        get_user_info_using_access_token(self.login_username, self.otp_seed, access_token)
        self.logger.info('testSecret: Successfully tested secret')

    def finish_secret(self):
        """
        Finalize the secret rotation and delete the old access token from the account
        Raises:
            ResourceNotFoundException: If the secret with the specified arn does not exist
            HttpError: If the old access token deletion fails
        """
        access_token = get_secret_value(self.service_client, self.secret_config)

        super(UserAccessTokenRotator, self).finish_secret()

        # delete the old access token post rotation
        delete_access_token(self.login_username, self.otp_seed, self.login_password, access_token)
        self.logger.info('finishSecret: Successfully finalized secret rotation')

    def get_access_token_secret_config(self):
        """
        Match the arn with the specified access token secrets in secrets_config.json
        Returns the secret configuration dictionary if found
        Args:
            arn (string): The unique arn of the secret
        Raises:
            KeyError: If the arn cannot be found in the configuration
        """
        try:
            access_token_secrets_configs = get_access_token_secrets_configs('npm_access_token_secrets')
            for secret_config in access_token_secrets_configs:
                if secret_config['arn'] == self.arn:
                    return secret_config
                else:
                    raise KeyError(
                        'The secret arn cannot be found in the list of access token secrets from config'
                    )
        except KeyError as e:
            self.logger.error(
                'The secret arn could not be matched with any known access token secrets from config')
            raise e
