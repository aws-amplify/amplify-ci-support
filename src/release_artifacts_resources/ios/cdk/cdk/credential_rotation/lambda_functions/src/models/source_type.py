from enum import Enum

class SourceType(Enum):
    """The source of a value to push to a destination
    """
    AWS_SESSION_CREDENTIALS = "aws_session_credentials"

    SECRETS_MANAGER = "secrets_manager"

    LAMBDA_ENVIRONMENT_VARIABLE = "lambda_environment_variable"
