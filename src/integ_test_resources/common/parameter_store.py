from aws_cdk import aws_ssm, core

from common.platforms import Platform


def save_string_parameter(scope: core.Stack,
                          key: str,
                          value: str,
                          platform: Platform) -> None:
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

    # Parameter names cannot be prefixed with the token 'aws', thus it is
    # conspicuously absent from the namespace. See: https://amzn.to/2VDaqtC
    NAMESPACE = ('mobile-sdk', platform.value)

    tail = (scope.stack_name, key)
    resource_id = "param_" + key
    parameter_name = '/' + '/'.join(NAMESPACE + tail)
    print(parameter_name)

    aws_ssm.StringParameter(scope,
                            resource_id,
                            string_value=value,
                            parameter_name=parameter_name,
                            simple_name=False)
