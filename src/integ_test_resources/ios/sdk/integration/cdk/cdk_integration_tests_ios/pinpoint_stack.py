from aws_cdk import(
    core,
    aws_pinpoint,
    aws_iam
)

from parameter_store import save_string_parameter

class PinpointStack(core.Stack):

    def __init__(self,
                 scope: core.Construct,
                 id: str,
                 circleci_execution_role: aws_iam.Role,
                 **kwargs) -> None:
        super().__init__(scope,
                         id,
                         **kwargs)

        app = aws_pinpoint.CfnApp(self,
                                  "integ_test_app",
                                  name="integ_test_app")

        save_string_parameter(self,
                              "pinpointAppId",
                              app.ref)

        circleci_execution_role.add_to_policy(aws_iam.PolicyStatement(effect=aws_iam.Effect.ALLOW,
                                                                      actions=[
                                                                          "mobileanalytics:putEvents",
                                                                          "mobiletargeting:PutEvents",
                                                                          "mobiletargeting:UpdateEndpoint"
                                                                      ],
                                                                      resources=["*"]))
        self._app = app

    # @property
    # def app(self) -> aws_pinpoint.CfnApp:
    #     return self._app
    #
    # @app.setter
    # def app(self, value):
    #     self._app = value