import json
from aws_cdk import(
    core,
    aws_iam
)
from common.auth_utils import construct_identity_pool
from common.common_stack import CommonStack
from common.region_aware_stack import RegionAwareStack
from common.platforms import Platform
from common.secrets_manager import get_integ_tests_secrets

class CoreStack(RegionAwareStack):

    def __init__(self,
                 scope: core.Construct,
                 id: str,
                 common_stack: CommonStack,
                 **kwargs) -> None:

        super().__init__(scope,
                         id,
                         **kwargs)

        self._supported_in_region = self.are_services_supported_in_region(["cognito-identity"])

        (self._facebook_app_id, self._facebook_app_secret) = self.get_facebook_app_config()

        (identity_pool_with_facebook,
         identity_pool_auth_role,
         identity_pool_unauth_role) = self.construct_identity_pool_with_facebook_as_idp()

        (unauth_identity_pool, _, _) = construct_identity_pool(self,
                                                               resource_id_prefix="core2",
                                                               auth_role=identity_pool_auth_role,
                                                               unauth_role=identity_pool_unauth_role
                                                              )

        self._parameters_to_save = {
            "identityPoolId": identity_pool_with_facebook.ref,
            "unauthIdentityPoolId": unauth_identity_pool.ref,
            "authRoleArn": identity_pool_auth_role.role_arn,
            "unauthRoleArn": identity_pool_unauth_role.role_arn,
            "facebookAppId": self._facebook_app_id,
            "facebookAppSecret": self._facebook_app_secret
        }

        self.create_wic_provider_test_role()

        stack_policy = aws_iam.PolicyStatement(effect=aws_iam.Effect.ALLOW,
                                                actions=[
                                                    "cognito-identity:*",
                                                ],
                                                resources=["*"])

        common_stack.add_to_common_role_policies(self,
                                                 policy_to_add=stack_policy)

        self.save_parameters_in_parameter_store()

    def get_facebook_app_config(self) -> tuple:

        ios_integ_tests_secrets = json.loads(get_integ_tests_secrets(platform=Platform.IOS))
        facebook_app_id = ios_integ_tests_secrets["IOS_FB_AWSCORETESTS_APP_ID"],
        facebook_app_secret = ios_integ_tests_secrets["IOS_FB_AWSCORETESTS_APP_SECRET"]
        return (facebook_app_id, facebook_app_secret)

    def construct_identity_pool_with_facebook_as_idp(self) -> tuple:

        supported_login_providers = {
            "graph.facebook.com": self._facebook_app_id
        }
        construct_identity_pool(self,
                                resource_id_prefix="core",
                                supported_login_providers=supported_login_providers,
                                developer_provider_name="iostests.com"
                                )

    def create_wic_provider_test_role(self) -> None:
        wic_provider_test_role_condition = {
            "StringEquals": {
                "graph.facebook.com:app_id": self._facebook_app_id
            }
        }

        wic_provider_test_role = aws_iam.Role(self,
                                              "wic_provider_test_role",
                                              assumed_by=aws_iam.FederatedPrincipal("graph.facebook.com",
                                                                                    wic_provider_test_role_condition,
                                                                                    "sts:AssumeRoleWithWebIdentity")
                                              )
        wic_provider_test_role.add_to_policy(aws_iam.PolicyStatement(
            effect=aws_iam.Effect.ALLOW,
            actions=[
                "translate:TranslateText",
            ],
            resources=["*"]
        ))

        self.parameters_to_save["WICProviderTestRoleArn"] = wic_provider_test_role.role_arn



