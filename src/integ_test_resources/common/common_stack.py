from aws_cdk import aws_cognito, aws_iam, core

from common.auth_utils import construct_identity_pool
from common.platforms import Platform
from common.region_aware_stack import RegionAwareStack
from common.github_action_oidc import GithubActionOIDC

class CommonStack(RegionAwareStack):
    def __init__(self, scope: core.Construct, id: str, platform: Platform, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        circleci_execution_role = aws_iam.Role(
            self,
            "circleci_execution_role",
            assumed_by=aws_iam.AccountPrincipal(self.account),
            max_session_duration=core.Duration.hours(4),
        )

        policy_to_add = aws_iam.PolicyStatement(
            effect=aws_iam.Effect.ALLOW,
            actions=["ssm:GetParameter", "ssm:GetParametersByPath"],
            resources=["*"],
        )
        circleci_execution_role.add_to_policy(policy_to_add)

        self._circleci_execution_role = circleci_execution_role
        self._supported_in_region = True
        self._cognito_support_in_region = self.is_cognito_supported_in_region()

        self._parameters_to_save = {
            "circleci_execution_role": circleci_execution_role.role_arn,
            "cognito_support_in_region": str(self._cognito_support_in_region),
        }

        if self._cognito_support_in_region:
            self.create_common_identity_pool()

        self.save_parameters_in_parameter_store(platform=platform)
        if platform == Platform.IOS:
            self.github_action_oidc = GithubActionOIDC(self, "github_action_oidc")
            self.github_action_oidc.aws_sdk_ios_integration_test_role.add_to_policy(policy_to_add)

    def is_cognito_supported_in_region(self, region_name: str = None) -> bool:
        return self.is_service_supported_in_region("cognito-identity", region_name=region_name)

    def add_to_common_role_policies(
        self, scope: core.Stack, policy_to_add: aws_iam.PolicyStatement = None
    ) -> None:
        if policy_to_add is None:
            policy_to_add = aws_iam.PolicyStatement(
                effect=aws_iam.Effect.ALLOW,
                actions=["{}:*".format(scope.stack_name)],
                resources=["*"],
            )

        self._circleci_execution_role.add_to_policy(policy_to_add)
        if self.github_action_oidc is not None:
            self.github_action_oidc.aws_sdk_ios_integration_test_role.add_to_policy(policy_to_add)


        if self._cognito_support_in_region:
            self._cognito_identity_pool_auth_role.add_to_policy(policy_to_add)
            self._cognito_identity_pool_unauth_role.add_to_policy(policy_to_add)

    def create_common_identity_pool(self) -> None:
        (
            cognito_identity_pool,
            cognito_identity_pool_auth_role,
            cognito_identity_pool_unauth_role,
        ) = construct_identity_pool(self, "common")
        self._cognito_identity_pool = cognito_identity_pool
        self._cognito_identity_pool_auth_role = cognito_identity_pool_auth_role
        self._cognito_identity_pool_unauth_role = cognito_identity_pool_unauth_role
        self.parameters_to_save["identityPoolId"] = cognito_identity_pool.ref
        self.parameters_to_save["authRoleArn"] = cognito_identity_pool_auth_role.role_arn
        self.parameters_to_save["unauthRoleArn"] = cognito_identity_pool_unauth_role.role_arn
        self.parameters_to_save["region"] = self.node.try_get_context("region")

    @property
    def circleci_execution_role(self) -> aws_iam.Role:
        return self._circleci_execution_role

    @property
    def cognito_identity_pool(self) -> aws_cognito.CfnIdentityPool:
        return self._cognito_identity_pool

    @property
    def cognito_identity_pool_auth_role(self) -> aws_iam.Role:
        return self._cognito_identity_pool_auth_role

    @property
    def cognito_identity_pool_unauth_role(self) -> aws_iam.Role:
        return self._cognito_identity_pool_unauth_role
