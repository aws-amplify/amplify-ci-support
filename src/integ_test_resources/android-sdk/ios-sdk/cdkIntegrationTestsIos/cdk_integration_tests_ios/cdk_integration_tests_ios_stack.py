from aws_cdk import(
    core,
    aws_lambda as _lambda,
    aws_apigateway as apigw
)


class CdkIntegrationTestsIosStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        echo_lambda = _lambda.Function(
            self, 'EchoHandler',
            runtime=_lambda.Runtime.PYTHON_3_7,
            code=_lambda.Code.asset('lambda'),
            handler='echo.handler',
        )

        apiEndpoint = apigw.LambdaRestApi(
                        self, 'apiEndpoint',
                        handler=echo_lambda,
                      )
