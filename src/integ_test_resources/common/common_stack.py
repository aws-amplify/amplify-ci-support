from aws_cdk import aws_iam
from aws_cdk import core

from common.parameters import string_parameter


class CommonStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope,
                         id,
                         **kwargs)

        circleci_execution_role = aws_iam.Role(
            self,
            'circleci_execution_role',
            assumed_by=aws_iam.AccountPrincipal(self.account),
            max_session_duration=core.Duration.hours(4))
        string_parameter(self,
                         'circleci_execution_role',
                         circleci_execution_role.role_arn)

        self._circleci_execution_role = circleci_execution_role

    @property
    def circleci_execution_role(self) -> aws_iam.Role:
        return self._circleci_execution_role

    @circleci_execution_role.setter
    def circleci_execution_role(self, value):
        self._circleci_execution_role = value
