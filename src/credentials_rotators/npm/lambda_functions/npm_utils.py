import pyotp
import requests
import json


def generate_otp(username, otp_seed):
    """Generate a time based OTP using the OTP_SEED for the npm user
    It is used in 2 Factor Authentication for the user account
    Args:
        username (string): The username of the npm user
        otp_seed (string): The seed generated during 2 factor auth setup for the user
    """
    totp = pyotp.parse_uri(f'otpauth://totp/{username}?secret={otp_seed}&issuer=npm')
    otp = totp.now()
    print(f'otp is: {otp}')
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
    print(f"otp:{otp}")

    headers = {
        'content-type': 'application/json',
        'npm-otp': otp
    }

    url = 'https://registry.npmjs.org/-/npm/v1/user'
    data_dict = {'password': {'old': current_password, 'new': new_password}}
    data = json.dumps(data_dict)
    print(f'data: {data}')

    response = requests.post(url, headers=headers, data=data, auth=(username, current_password))
    print(response)
    response.raise_for_status()


def get_user_info(username, otp_seed, password):
    """Fetch the npm user profile information
    Args:
        username (string): The username of the npm user
        otp_seed (string): The seed generated during 2 factor auth setup for the user
        password (string): The current active login password for the npm user
    Raises:
        HttpError: If the user profile information cannot be fetched
    """
    otp = generate_otp(username, otp_seed)
    print(f"otp:{otp}")

    headers = {
        'content-type': 'application/json',
        'npm-otp': otp
    }

    url = 'https://registry.npmjs.org/-/npm/v1/user'
    print(f'user: {username} and pass: {password}')

    response = requests.get(url, headers=headers, auth=(username, password))
    print(response)
    response.raise_for_status()