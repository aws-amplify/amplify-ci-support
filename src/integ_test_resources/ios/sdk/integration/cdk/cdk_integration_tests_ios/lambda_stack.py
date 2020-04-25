from aws_cdk import(
    core,
    aws_lambda,
    aws_iam
)

class LambdaStack(core.Stack):

    def __init__(self,
                 scope: core.Construct,
                 id: str,
                 circleci_execution_role: aws_iam.Role,
                 **kwargs) -> None:

        super().__init__(scope, id, **kwargs)

        echo_function = aws_lambda.Function(
                                        self, "lambdaEcho",
                                        runtime=aws_lambda.Runtime.PYTHON_3_7,
                                        code=aws_lambda.Code.asset("lambda"),
                                        handler="echo.handler")
        core.CfnOutput(self, "echofunctionname", value=echo_function.function_name)
        self._lambda_echo_function = echo_function

        circleci_execution_role.add_to_policy(aws_iam.PolicyStatement(effect=aws_iam.Effect.ALLOW,
                                                                      actions=[
                                                                          "lambda:*"],
                                                                      resources=["*"]))

    @property
    def lambda_echo_function(self) -> aws_lambda.IFunction:
        return self._lambda_echo_function

    @lambda_echo_function.setter
    def lambda_echo_function(self, value):
        self._lambda_echo_function = value
