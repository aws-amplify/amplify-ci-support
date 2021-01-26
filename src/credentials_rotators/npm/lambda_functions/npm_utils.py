import pyotp
import requests
import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def generate_otp(username, otp_seed):
    """Generate a time based OTP using the OTP_SEED for the npm user
    It is used in 2 Factor Authentication for the user account
    Args:
        username (string): The username of the npm user
        otp_seed (string): The seed generated during 2 factor auth setup for the user
    """
    totp = pyotp.parse_uri(f'otpauth://totp/{username}?secret={otp_seed}&issuer=npm')
    otp = totp.now()
    return otp


def update_login_password(username, otp_seed, current_password, new_password):
    """Update the login password for the npm user
    Args:
        username (string): The username of the npm user
        otp_seed (string): The seed generated during 2 factor auth setup for the user
        current_password (string): The current active login password for the npm user
        new_password (string): The new login password to be set for the npm user
    Raises:
        HttpError: If the password update fails
    """
    otp = generate_otp(username, otp_seed)

    headers = {
        'content-type': 'application/json',
        'npm-otp': otp
    }

    url = 'https://registry.npmjs.org/-/npm/v1/user'
    data_dict = {'password': {'old': current_password, 'new': new_password}}
    data = json.dumps(data_dict)

    response = requests.post(url, headers=headers, data=data, auth=(username, current_password))
    response.raise_for_status()

def create_access_token(username, otp_seed, password):
    """Create an access token for a NPM user
    Args:
        username (string): The username of the npm user
        otp_seed (string): The seed generated during 2 factor auth setup for the user
        password (string): The current active login password for the npm user
    Raises:
        HttpError: If the access token creation fails
    """
    otp = generate_otp(username, otp_seed)

    headers = {
        'content-type': 'application/json',
        'npm-otp': otp
    }

    url = 'https://registry.npmjs.org/-/npm/v1/tokens'
    data_dict = {'password': password}
    data = json.dumps(data_dict)

    response = requests.post(url, headers=headers, data=data, auth=(username, password))
    response.raise_for_status()
    return json.loads(response.content)['token']


def get_user_info_using_password(username, otp_seed, password):
    """Fetch the npm user profile information after authorization using password and OTP
    Args:
        username (string): The username of the npm user
        otp_seed (string): The seed generated during 2 factor auth setup for the user
        password (string): The current active login password for the npm user
    Raises:
        HttpError: If the user profile information cannot be fetched
    """
    otp = generate_otp(username, otp_seed)

    headers = {
        'content-type': 'application/json',
        'npm-otp': otp
    }

    url = 'https://registry.npmjs.org/-/npm/v1/user'
    response = requests.get(url, headers=headers, auth=(username, password))
    response.raise_for_status()

def get_user_info_using_access_token(username, otp_seed, access_token):
    """Fetch the npm user profile information after authorization using access token and OTP
    Args:
        username (string): The username of the npm user
        otp_seed (string): The seed generated during 2 factor auth setup for the user
        access_token (string): The active access token for the npm user
    Raises:
        HttpError: If the user profile information cannot be fetched
    """
    otp = generate_otp(username, otp_seed)

    headers = {
        'Authorization': f'Bearer {access_token}',
        'content-type': 'application/json',
        'npm-otp': otp
    }

    url = 'https://registry.npmjs.org/-/npm/v1/user'
    response = requests.get(url, headers=headers)
    response.raise_for_status()

def delete_access_token(username, otp_seed, password, access_token):
    """Delete given access token for a NPM user
    Args:
        username (string): The username of the npm user
        otp_seed (string): The seed generated during 2 factor auth setup for the user
        password (string): The current active login password for the npm user
        access_token (string): The access_token to be deleted
    Raises:
        HttpError: If the access token creation fails
    """
    otp = generate_otp(username, otp_seed)

    headers = {
        'content-type': 'application/json',
        'npm-otp': otp
    }

    url = f'https://registry.npmjs.org/-/npm/v1/tokens/token/{access_token}'
    data_dict = {'password': password}
    data = json.dumps(data_dict)

    response = requests.delete(url, headers=headers, data=data, auth=(username, password))
    response.raise_for_status()

def check_access_token_exists(username, otp_seed, password, access_token, secret_id):
    """Check if the given access token is active for a NPM user
        Args:
            username (string): The username of the npm user
            otp_seed (string): The seed generated during 2 factor auth setup for the user
            password (string): The current active login password for the npm user
            access_token (string): The access_token to be deleted
            secret_id (string): Friendly identifier for the access token secret
        Raises:
            HttpError: If the access token creation fails
        """
    otp = generate_otp(username, otp_seed)

    headers = {
        'content-type': 'application/json',
        'npm-otp': otp
    }

    url = 'https://registry.npmjs.org/-/npm/v1/tokens'
    data_dict = {'password': password}
    data = json.dumps(data_dict)

    response = requests.get(url, headers=headers, data=data, auth=(username, password))
    response.raise_for_status()
    print(f'response from list tokens: {json.loads(response.text)}')

    active_tokens = [object['token'] for object in json.loads(response.content)['objects']]
    print(f'active_tokens: {active_tokens}')
    try:
        active_tokens.index(access_token)
    except ValueError as e:
        logger.info(f'Failed to verify that access token ({secret_id}) is correctly added')
