from typing import List, Union

from aws_cdk import aws_ssm as ssm
from aws_cdk import Stack
from common.platforms import Platform


def save_parameter(
    scope: Stack, key: str, value: Union[str, List[str]], platform: Platform
) -> None:
    """
    Saves a parameter to the Amazon Systems Manager Parameter Store. The value
    can be either a scalar string or a list of string
    This method saves the given value under a key. Scopes passed to this method
    must include a `stack` attribute which is used in forming the fully
    qualified parameter name.
    The fully qualified parameter name will always start with mobile-sdk and
    android, followed by the stack name, and the passed key name. For example,
    if the apigateway stack calls save_parameter with a key name of api_name,
    the resulting fully qualified parameter name would be:
    /mobile-sdk/android/apigateway/api_name
    """
    if type(value) is list:
        save_string_list_parameter(scope, key, value, platform)
    else:
        save_string_parameter(scope, key, value, platform)


def save_string_parameter(scope: Stack, key: str, value: str, platform: Platform) -> None:
    """
    Saves a string parameter to the Amazon Systems Manager Parameter Store.
    This method saves the given value under a key. Scopes passed to this method
    must include a `stack` attribute which is used in forming the fully
    qualified parameter name.
    The fully qualified parameter name will always start with mobile-sdk and
    android, followed by the stack name, and the passed key name. For example,
    if the apigateway stack calls save_parameter with a key name of api_name,
    the resulting fully qualified parameter name would be:
    /mobile-sdk/android/apigateway/api_name
    """

    resource_id = "param_" + key
    parameter_name = _get_parameter_name(platform, scope, key)

    ssm.StringParameter(
        scope, resource_id, string_value=value, parameter_name=parameter_name, simple_name=False
    )


def save_string_list_parameter(
    scope: Stack, key: str, value: [str], platform: Platform
) -> None:
    """
    Saves a string list parameter to the Amazon Systems Manager Parameter Store.
    This method saves the given value under a key. Scopes passed to this method
    must include a `stack` attribute which is used in forming the fully
    qualified parameter name.
    The fully qualified parameter name will always start with mobile-sdk and
    android, followed by the stack name, and the passed key name. For example,
    if the apigateway stack calls save_parameter with a key name of api_name,
    the resulting fully qualified parameter name would be:
    /mobile-sdk/android/apigateway/api_name
    """

    resource_id = "param_" + key
    parameter_name = _get_parameter_name(platform, scope, key)

    ssm.StringListParameter(
        scope,
        resource_id,
        string_list_value=value,
        parameter_name=parameter_name,
        simple_name=False,
    )


def _get_parameter_name(platform: Platform, scope: Stack, key: str) -> str:
    # Parameter names cannot be prefixed with the token 'aws', thus it is
    # conspicuously absent from the namespace. See: https://amzn.to/2VDaqtC
    namespace = ("mobile-sdk", platform.value)

    tail = (scope.stack_name, key)
    parameter_name = "/" + "/".join(namespace + tail)
    return parameter_name
