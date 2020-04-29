from aws_cdk import(
    core,
    aws_iam,
    aws_cognito
)

from parameter_store import save_string_parameter
from auth_utils import construct_identity_pool
from cdk_stack_extension import CDKStackExtension

class CommonStack(CDKStackExtension):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope,
                         id,
                         **kwargs)

        circleci_execution_role = aws_iam.Role(self,
                                               "circleci_execution_role",
                                               assumed_by=aws_iam.AccountPrincipal(self.account))

        self._circleci_execution_role = circleci_execution_role
        self._supported_in_region = True
        self._cognito_support_in_region = self.is_cognito_supported_in_region()
        parameters_to_save = {
            "circleci_execution_role": circleci_execution_role.role_arn,
            "cognito_support_in_region": str(self._cognito_support_in_region)
        }

        if self._cognito_support_in_region:
            (cognito_identity_pool,
             cognito_identity_pool_auth_role,
             cognito_identity_pool_unauth_role) = construct_identity_pool(self,
                                                                          "common")
            self._cognito_identity_pool = cognito_identity_pool
            self._cognito_identity_pool_auth_role = cognito_identity_pool_auth_role
            self._cognito_identity_pool_unauth_role = cognito_identity_pool_unauth_role
            parameters_to_save["identityPoolId"] = cognito_identity_pool.ref
            parameters_to_save["authRoleArn"] = cognito_identity_pool_auth_role.role_arn
            parameters_to_save["unauthRoleArn"] = cognito_identity_pool_auth_role.role_arn

        for parameter_name, parameter_value in parameters_to_save.items():
            save_string_parameter(self,
                                  parameter_name,
                                  parameter_value)


    def is_cognito_supported_in_region(self,
                                       region_name:str = None) -> bool:
        return self.is_service_supported_in_region("cognito-identity",
                                                   region_name=region_name)

    def add_to_common_role_policies(self,
                                    scope: core.Stack,
                                    policy_to_add: aws_iam.PolicyStatement = None) -> None:
        if policy_to_add is None:
            policy_to_add = aws_iam.PolicyStatement(effect=aws_iam.Effect.ALLOW,
                                                    actions=[
                                                        "{}:*".format(scope.stack_name)],
                                                    resources=["*"])

        self._circleci_execution_role.add_to_policy(policy_to_add)

        if self._cognito_support_in_region:
            self._cognito_identity_pool_auth_role.add_to_policy(policy_to_add)
            self._cognito_identity_pool_unauth_role.add_to_policy(policy_to_add)

    @property
    def circleci_execution_role(self) -> aws_iam.Role:
        return self._circleci_execution_role

    @circleci_execution_role.setter
    def circleci_execution_role(self, value):
        self._circleci_execution_role = value

    @property
    def cognito_identity_pool(self) -> aws_cognito.CfnIdentityPool:
        return self._cognito_identity_pool

    @cognito_identity_pool.setter
    def cognito_identity_pool(self, value):
        self._cognito_identity_pool = value

    @property
    def cognito_identity_pool_auth_role(self) -> aws_iam.Role:
        return self._cognito_identity_pool_auth_role

    @cognito_identity_pool_auth_role.setter
    def cognito_identity_pool_auth_role(self, value):
        self._cognito_identity_pool_auth_role = value

    @property
    def cognito_identity_pool_unauth_role(self) -> aws_iam.Role:
        return self._cognito_identity_pool_unauth_role

    @cognito_identity_pool_unauth_role.setter
    def cognito_identity_pool_unauth_role(self, value):
        self._cognito_identity_pool_unauth_role = value

