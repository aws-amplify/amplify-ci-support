from secret_rotator import SecretRotator
from secrets_config_utils import get_secret_config
from secrets_manager_utils import get_secret_value


class NPMCredentialsRotator(SecretRotator):
    """
    Holds the attributes and methods common to all NPM user credential rotators
    """

    def __init__(self, arn, token, step):
        super().__init__(arn, token, step)

        # Secrets that are commonly used by NPM credential rotators for authentication etc.
        # This avoids fetching these inside every method and thereby making less network calls
        self.login_username = get_secret_value(self.service_client, get_secret_config('npm_login_username_secret'))
        self.otp_seed = get_secret_value(self.service_client, get_secret_config('npm_otp_seed_secret'))
        self.login_password = get_secret_value(self.service_client, get_secret_config('npm_login_password_secret'))
