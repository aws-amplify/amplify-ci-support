from aws_cdk import(
    core,
    aws_cloudformation,
    aws_cognito,
    aws_iam
)
from parameter_store import save_string_parameter
from auth_utils import construct_identity_pool
from common_stack import CommonStack
from cdk_stack_extension import CDKStackExtension

class MobileClientStack(CDKStackExtension):

    def __init__(self,
                 scope: core.Construct,
                 id: str,
                 common_stack: CommonStack,
                 **kwargs) -> None:

        super().__init__(scope,
                         id,
                         **kwargs)

        self._supported_in_region = self.is_service_supported_in_region("cognito-identity")

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

        save_string_parameter(self, "userpool_id", user_pool.user_pool_id)
        save_string_parameter(self, "pool_id_dev_auth", identity_pool.ref)

        stack_policy = aws_iam.PolicyStatement(effect=aws_iam.Effect.ALLOW,
                                               actions=[
                                                   "cognito-identity:*",
                                               ],
                                               resources=["*"])

        common_stack.add_to_common_role_policies(self, policy_to_add=stack_policy)
