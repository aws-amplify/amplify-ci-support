from aws_cdk import aws_cognito, aws_iam, core

from common.auth_utils import construct_identity_pool
from common.common_stack import CommonStack
from common.platforms import Platform
from common.region_aware_stack import RegionAwareStack


class MobileClientStack(RegionAwareStack):

    def __init__(self,
                 scope: core.Construct,
                 id: str,
                 common_stack: CommonStack,
                 **kwargs) -> None:

        super().__init__(scope,
                         id,
                         **kwargs)

        self._supported_in_region = self.are_services_supported_in_region(["cognito-identity",
                                                                           "cognito-idp"])

        user_pool = aws_cognito.UserPool(self,
                                         "userpool",
                                         required_attributes=aws_cognito.RequiredAttributes(email=True),
                                         self_sign_up_enabled=True,
                                         auto_verify=aws_cognito.AutoVerifiedAttrs(email=True))

        user_pool_client = aws_cognito.UserPoolClient(self,
                                                      "userpool_client",
                                                      generate_secret=False,
                                                      user_pool=user_pool)

        cognito_identity_providers = [{
            "clientId": user_pool_client.user_pool_client_id,
            "providerName": user_pool.user_pool_provider_name
        }]

        (identity_pool, _, _) = construct_identity_pool(self,
                                                        resource_id_prefix="mobileclient",
                                                        cognito_identity_providers = cognito_identity_providers,
                                                        )

        self._parameters_to_save = {
            "userpool_id": user_pool.user_pool_id,
            "pool_id_dev_auth": identity_pool.ref
        }
        self.save_parameters_in_parameter_store(platform=Platform.IOS)

        stack_policy = aws_iam.PolicyStatement(effect=aws_iam.Effect.ALLOW,
                                               actions=[
                                                   "cognito-identity:*",
                                               ],
                                               resources=["*"])

        common_stack.add_to_common_role_policies(self, policy_to_add=stack_policy)
