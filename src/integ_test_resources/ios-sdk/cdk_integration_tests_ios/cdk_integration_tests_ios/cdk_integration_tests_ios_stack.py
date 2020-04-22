from aws_cdk import(
    core,
    aws_lambda,
    aws_apigateway
)


class CdkIntegrationTestsIosStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        echo_lambda = aws_lambda.Function(
            self, 'EchoHandler',
            runtime=aws_lambda.Runtime.PYTHON_3_7,
            code=aws_lambda.Code.asset('lambda'),
            handler='echo.handler',
        )

        apiEndpoint = aws_apigateway.LambdaRestApi(
                        self, 'apiEndpoint',
                        handler=echo_lambda,
                      )
