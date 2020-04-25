from aws_cdk import core
from aws_cdk import aws_ssm as ssm

# Parameter names cannot be prefixed with the token 'aws', thus it is
# conspicuously absent from the namespace. See: https://amzn.to/2VDaqtC
NAMESPACE = ('mobile-sdk', 'android')


def string_parameter(
        scope: core.Construct,
        key: str,
        value: str
) -> ssm.StringParameter:
    """
    Saves a string parameter to the AWS Systems Manager Parameter Store.

    This method saves the given value under a key. Scopes passed to this method
    must include a `stack` attribute which is used in forming the fully
    qualified parameter name.

    The fully qualified parameter name will always start with mobile-sdk and
    android, followed by the stack name, and the passed key name. For example,
    if the apigateway stack calls save_parameter with a key name of api_name,
    the resulting fully qualified parameter name would be:

    /mobile-sdk/android/apigateway/api_name
    """
    tail = (scope.stack, key)
    resource_id = '_'.join(tail)
    fqpn = '/' + '/'.join(NAMESPACE + tail)

    return ssm.StringParameter(scope, resource_id, string_value=value,
                               parameter_name=fqpn)
