from enum import Enum


class DestinationType(str, Enum):
    """A destination that rotated values are pushed to"""

    CIRCLECI_ENVIRONMENT_VARIABLE = "cci_env_variable"
