from aws_cdk import aws_iam as iam
from aws_cdk import aws_cognito as cognito
from constructs import Construct
from common.auth_utils import construct_identity_pool
from common.common_stack import CommonStack
from common.platforms import Platform
from common.region_aware_stack import RegionAwareStack
from common.secrets_manager import get_integ_tests_secrets


class CoreStack(RegionAwareStack):
    def __init__(self, scope: Construct, id: str, common_stack: CommonStack, **kwargs) -> None:

        super().__init__(scope, id, **kwargs)

        self._supported_in_region = self.are_services_supported_in_region(["cognito-identity"])

        (self._facebook_app_id, self._facebook_app_secret) = CoreStack.get_facebook_app_config()

        supported_login_providers = {"graph.facebook.com": self._facebook_app_id}
        (
            identity_pool_with_facebook,
            identity_pool_auth_role,
            identity_pool_unauth_role,
        ) = construct_identity_pool(
            self,
            resource_id_prefix="core",
            supported_login_providers=supported_login_providers,
            developer_provider_name="iostests.com",
        )

        (unauth_identity_pool, _, _) = construct_identity_pool(
            self,
            resource_id_prefix="core2",
            auth_role=identity_pool_auth_role,
            unauth_role=identity_pool_unauth_role,
        )

        self._parameters_to_save = {
            "identityPoolId": identity_pool_with_facebook.ref,
            "unauthIdentityPoolId": unauth_identity_pool.ref,
            "authRoleArn": identity_pool_auth_role.role_arn,
            "unauthRoleArn": identity_pool_unauth_role.role_arn,
            "facebookAppId": self._facebook_app_id,
            "facebookAppSecret": self._facebook_app_secret,
        }

        self.create_wic_provider_test_role()

        stack_policy = iam.PolicyStatement(
            effect=iam.Effect.ALLOW, actions=["cognito-identity:*"], resources=["*"]
        )

        common_stack.add_to_common_role_policies(self, policy_to_add=stack_policy)

        self.save_parameters_in_parameter_store(platform=Platform.IOS)

    @staticmethod
    def get_facebook_app_config() -> (str, str):
        ios_integ_tests_secrets = get_integ_tests_secrets(platform=Platform.IOS)
        facebook_app_id = ios_integ_tests_secrets["facebook.app_id"]
        facebook_app_secret = ios_integ_tests_secrets["facebook.app_secret"]
        return facebook_app_id, facebook_app_secret

    def construct_identity_pool_with_facebook_as_idp(
        self,
    ) -> (cognito.CfnIdentityPool, iam.Role, iam.Role):

        supported_login_providers = {"graph.facebook.com": self._facebook_app_id}
        (identity_pool, auth_role, unauth_role) = construct_identity_pool(
            self,
            resource_id_prefix="core",
            supported_login_providers=supported_login_providers,
            developer_provider_name="iostests.com",
        )
        return (identity_pool, auth_role, unauth_role)

    def create_wic_provider_test_role(self) -> None:
        wic_provider_test_role_condition = {
            "StringEquals": {"graph.facebook.com:app_id": self._facebook_app_id}
        }

        wic_provider_test_role = iam.Role(
            self,
            "wic_provider_test_role",
            assumed_by=iam.FederatedPrincipal(
                "graph.facebook.com",
                wic_provider_test_role_condition,
                "sts:AssumeRoleWithWebIdentity",
            ),
        )
        wic_provider_test_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW, actions=["translate:TranslateText"], resources=["*"]
            )
        )

        self.parameters_to_save["WICProviderTestRoleArn"] = wic_provider_test_role.role_arn
