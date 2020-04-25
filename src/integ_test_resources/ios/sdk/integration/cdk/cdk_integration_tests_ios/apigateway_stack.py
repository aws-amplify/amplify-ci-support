from aws_cdk import(
    core,
    aws_lambda,
    aws_apigateway,
    aws_cloudformation,
    aws_iam
)


class ApigatewayStack(core.Stack):

    def __init__(self,
                 scope: core.Construct,
                 id: str,
                 lambda_echo: aws_lambda.Function,
                 circleci_execution_role: aws_iam.Role,
                 **kwargs) -> None:

        super().__init__(scope, id, **kwargs)

        endpoint = aws_apigateway.LambdaRestApi(self,
                                                "endpoint",
                                                handler=lambda_echo)
        core.CfnOutput(self, "endpointurl", value=endpoint.url)

        circleci_execution_role.add_to_policy(aws_iam.PolicyStatement(effect=aws_iam.Effect.ALLOW,
                                                                      actions=[
                                                                          "apigateway:*"],
                                                                      resources=["*"]))


