from user_login_password_rotator import UserLoginPasswordRotator
from user_access_token_rotator import UserAccessTokenRotator

def rotate_access_keys(event, context):
    """ Handler for lambda that rotates the npm user's access keys
    Args:
        event (dict): Lambda dictionary of event parameters. These keys must include the following:
            - SecretId: The secret ARN or identifier
            - ClientRequestToken: The ClientRequestToken of the secret version
            - Step: The rotation step (one of createSecret, setSecret, testSecret, or finishSecret)
        context (LambdaContext): The Lambda runtime information
    Raises:
        ResourceNotFoundException: If the secret with the specified arn and stage does not exist
        ValueError: If the secret is not properly configured for rotation
        KeyError: If the event parameters do not contain the expected keys
    """

    arn = event['SecretId']
    token = event['ClientRequestToken']
    step = event['Step']

    user_access_token_rotator = UserAccessTokenRotator(arn, token, step)
    user_access_token_rotator.rotate()


def rotate_login_password(event, context):
    """  Handler for lambda that rotates the npm user's login password
    Args:
        event (dict): Lambda dictionary of event parameters. These keys must include the following:
            - SecretId: The secret ARN or identifier
            - ClientRequestToken: The ClientRequestToken of the secret version
            - Step: The rotation step (one of createSecret, setSecret, testSecret, or finishSecret)
        context (LambdaContext): The Lambda runtime information
    Raises:
        ResourceNotFoundException: If the secret with the specified arn and stage does not exist
        ValueError: If the secret is not properly configured for rotation
        KeyError: If the event parameters do not contain the expected keys
    """
    arn = event['SecretId']
    token = event['ClientRequestToken']
    step = event['Step']

    user_login_password_rotator = UserLoginPasswordRotator(arn, token, step)
    user_login_password_rotator.rotate()
