from aws_cdk import aws_cognito
from aws_cdk import aws_iam
from aws_cdk import aws_lambda
from aws_cdk import core

from common.common_stack import CommonStack
from common.platforms import Platform
from common.region_aware_stack import RegionAwareStack


class IotStack(RegionAwareStack):
    """
    The iOS version of this stack works a little differently. It will
    generate a custom authorizer in the CDK. The Android tests create
    the custom authorizer _from the client._ Both the iOS and Android
    CDK scripts *do* create a lambda function, though. The Android IoT
    stack, here, will output the ARN of the lambda function so that it
    may be referenced by the client, to complete resource construction.
    """

    def __init__(self, scope: core.Construct, id: str, common_stack: CommonStack, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        self._supported_in_region = self.is_service_supported_in_region()

        self._parameters_to_save = {}

        self.setup_identity_pool()
        self.setup_custom_authorizer()

        self.save_parameters_in_parameter_store(platform=Platform.ANDROID)

        stack_policy = aws_iam.PolicyStatement(
            effect=aws_iam.Effect.ALLOW, actions=["cognito-identity:*", "iot:*"], resources=["*"]
        )
        common_stack.add_to_common_role_policies(self, policy_to_add=stack_policy)


    def setup_identity_pool(self):
        identity_pool = aws_cognito.CfnIdentityPool(
            self, "pinpoint_integ_test_android", allow_unauthenticated_identities=True
        )

        unauthenticated_role = aws_iam.Role(
            self,
            "CognitoDefaultUnauthenticatedRole",
            assumed_by=aws_iam.FederatedPrincipal(
                "cognito-identity.amazonaws.com",
                {
                    "StringEquals": {"cognito-identity.amazonaws.com:aud": identity_pool.ref},
                    "ForAnyValue:StringLike": {
                        "cognito-identity.amazonaws.com:amr": "unauthenticated"
                    },
                },
                "sts:AssumeRoleWithWebIdentity",
            ),
        )
        unauthenticated_role.add_to_policy(
            aws_iam.PolicyStatement(
                effect=aws_iam.Effect.ALLOW,
                actions=[
                    "cognito-sync:*",
                    "iot:*"
                ],
                resources=["*"],
            )
        )
        aws_cognito.CfnIdentityPoolRoleAttachment(
            self,
            "DefaultValid",
            identity_pool_id=identity_pool.ref,
            roles={"unauthenticated": unauthenticated_role.role_arn},
        )

        self._parameters_to_save["identity_pool_id"] = identity_pool.ref


    def setup_custom_authorizer(self):
        # Note: "key" is a bit overloaded here. In the context of the custom authorizer, "key name"
        # refers to the HTTP header field that the custom authorizer looks for a token value in.
        #
        # In the case of the custom authorizer key provider, the "key" is the KMS asymmetric CMK
        # used to sign the token value passed in the `token_key_name` header. In order to keep the
        # terminology consistent between client integ tests that are expecting to pass something for
        # a "key name" field, we'll let the ambiguity stand.
        token_key_name = "iot_custom_authorizer_token"
        self._parameters_to_save["custom_authorizer_token_key_name"] = token_key_name

        token_value = "allow"
        self._parameters_to_save["custom_authorizer_token_value"] = token_value

        authorizer_function_arn = self.setup_custom_authorizer_function()
        self._parameters_to_save["custom_authorizer_lambda_arn"] = authorizer_function_arn


    def setup_custom_authorizer_function(self) -> str:
        """
        Sets up the authorizer Lambda, and grants 'lambda:InvokeFunction' to the service principal
        'iot.amazonaws.com'

        :return: the ARN of the created function
        """
        authorizer_function = aws_lambda.Function(
            self,
            "iot_custom_authorizer_function",
            runtime=aws_lambda.Runtime.PYTHON_3_7,
            code=aws_lambda.Code.asset("custom_resources/iot_custom_authorizer_function"),
            handler="iot_custom_authorizer.handler",
            description="Sample custom authorizer that allows or denies based on 'token' value",
            current_version_options=aws_lambda.VersionOptions(
                removal_policy=core.RemovalPolicy.DESTROY
            ),
            environment={"RESOURCE_ARN": f"arn:aws:iot:{self.region}:{self.account}:*"},
        )
        authorizer_function.grant_invoke(aws_iam.ServicePrincipal("iot.amazonaws.com"))
        return authorizer_function.function_arn

