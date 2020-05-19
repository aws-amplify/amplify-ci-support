from typing import List, Optional

from aws_cdk import aws_cognito, aws_iam, aws_lambda, aws_s3, core, custom_resources

from common.auth_utils import construct_identity_pool
from common.common_stack import CommonStack
from common.platforms import Platform
from common.region_aware_stack import RegionAwareStack
from common.secrets_manager import get_integ_tests_secrets


class MobileClientStack(RegionAwareStack):
    DEVELOPER_PROVIDER_NAME = "login.test.awsmobileclient"
    """Used as the name of the developer-authenticated identity provider"""

    def __init__(self, scope: core.Construct, id: str, common_stack: CommonStack, **kwargs) -> None:

        super().__init__(scope, id, **kwargs)

        self._supported_in_region = self.are_services_supported_in_region(
            ["cognito-identity", "cognito-idp"]
        )

        if not self._supported_in_region:
            return

        self._secrets = get_integ_tests_secrets(platform=Platform.IOS)
        self._parameters_to_save["email_address"] = self._secrets["common.shared_email"]
        self._parameters_to_save["test_password"] = self._secrets["common.password"]

        self.update_common_stack_with_test_policy(common_stack)

        default_user_pool = self.create_user_pool("default", lambda_config=None)
        federation_providers = self.add_federation_to_user_pool(default_user_pool, "default")
        default_user_pool_client = self.create_user_pool_client(
            default_user_pool,
            "default",
            federation_providers
        )
        default_user_pool_client_secret = self.create_userpool_client_secret(
            default_user_pool, default_user_pool_client, "default"
        )
        default_user_pool_domain = self.create_user_pool_domain(default_user_pool, "default")
        self.update_parameters_for_userpool(
            default_user_pool,
            default_user_pool_client,
            default_user_pool_client_secret,
            default_user_pool_domain,
            "Default",
        )
        self.update_parameters_for_auth_section(
            default_user_pool_client,
            default_user_pool_client_secret,
            default_user_pool_domain,
            "Default",
        )
        # This is a special case parameter for custom auth tests
        self._parameters_to_save[
            "awsconfiguration/Auth/DefaultCustomAuth/authenticationFlowType"
        ] = "CUSTOM_AUTH"

        (identity_pool, auth_role, unauth_role) = construct_identity_pool(
            self,
            resource_id_prefix="mobileclient",
            cognito_identity_providers=[
                {
                    "clientId": default_user_pool_client.ref,
                    "providerName": f"cognito-idp.{self.region}.amazonaws.com/{default_user_pool.ref}",  # noqa: E501
                }
            ],
            developer_provider_name=MobileClientStack.DEVELOPER_PROVIDER_NAME,
        )
        self.update_parameters_for_identity_pool(identity_pool)

        s3_bucket = self.create_s3_bucket_and_policies(auth_role, unauth_role)
        self.update_parameters_for_s3_bucket(s3_bucket)

        custom_auth_lambda_configuration = self.create_custom_auth_lambda_configuration()
        custom_auth_user_pool = self.create_user_pool(
            "custom_auth", lambda_config=custom_auth_lambda_configuration
        )
        custom_auth_user_pool_client = self.create_user_pool_client(
            custom_auth_user_pool, "custom_auth", False
        )
        custom_auth_user_pool_client_secret = self.create_userpool_client_secret(
            custom_auth_user_pool, custom_auth_user_pool_client, "custom_auth"
        )
        self.update_parameters_for_userpool(
            custom_auth_user_pool,
            custom_auth_user_pool_client,
            custom_auth_user_pool_client_secret,
            None,
            "DefaultCustomAuth",
        )

        self.save_parameters_in_parameter_store(platform=Platform.IOS)

    def create_s3_bucket_and_policies(
        self, auth_role: aws_iam.Role, unauth_role: aws_iam.Role
    ) -> aws_s3.Bucket:
        """
        Creates an S3 bucket and storage policies that mimic Amplify configurations

        :param auth_role: The IAM role adopted by authenticated users the Identity Pool
        :param unauth_role: The IAM role adopted by unauthenticated users the Identity Pool
        :return: the S3 Bucket
        """
        bucket = aws_s3.Bucket(
            self, "integ_test_mobileclient_bucket", removal_policy=core.RemovalPolicy.DESTROY
        )
        MobileClientStack.add_public_policy(bucket, unauth_role, False)
        MobileClientStack.add_read_policy(bucket, unauth_role)
        MobileClientStack.add_list_policy(bucket, unauth_role, False)

        MobileClientStack.add_public_policy(bucket, auth_role, True)
        MobileClientStack.add_read_policy(bucket, auth_role)
        MobileClientStack.add_list_policy(bucket, auth_role, True)
        MobileClientStack.add_user_specific_policy(bucket, auth_role, "protected")
        MobileClientStack.add_user_specific_policy(bucket, auth_role, "private")
        MobileClientStack.add_uploads_policy(bucket, auth_role)

        return bucket

    def create_user_pool(
            self,
            tag: str,
            lambda_config: Optional[aws_cognito.CfnUserPool.LambdaConfigProperty]
    ) -> aws_cognito.CfnUserPool:
        user_pool = aws_cognito.CfnUserPool(
            self,
            f"userpool_{tag}",
            auto_verified_attributes=["email"],
            device_configuration=aws_cognito.CfnUserPool.DeviceConfigurationProperty(
                challenge_required_on_new_device=False, device_only_remembered_on_user_prompt=True
            ),
            schema=[
                aws_cognito.CfnUserPool.SchemaAttributeProperty(
                    attribute_data_type="String", mutable=False, name="email", required=True,
                ),
                aws_cognito.CfnUserPool.SchemaAttributeProperty(
                    attribute_data_type="String",
                    mutable=True,
                    name="mutableStringAttr1",
                    required=False,
                ),
                aws_cognito.CfnUserPool.SchemaAttributeProperty(
                    attribute_data_type="String",
                    mutable=True,
                    name="mutableStringAttr2",
                    required=False,
                ),
            ],
            lambda_config=lambda_config
        )
        return user_pool

    def add_federation_to_user_pool(
            self, user_pool: aws_cognito.CfnUserPool, tag: str
    ) -> List[aws_cognito.CfnUserPoolIdentityProvider]:
        facebook_identity_provider = aws_cognito.CfnUserPoolIdentityProvider(
            self,
            f"user_pool_idp_facebook_{tag}",
            provider_name="Facebook",
            provider_type="Facebook",
            user_pool_id=user_pool.ref,
            provider_details={
                "client_id": self._secrets["facebook.app_id"],
                "client_secret": self._secrets["facebook.app_secret"],
                "authorize_scopes": self._secrets["facebook.scopes"],
                "api_version": self._secrets["facebook.api_version"],
            },
            attribute_mapping={"email": "email", "username": "id"},
        )

        google_identity_provider = aws_cognito.CfnUserPoolIdentityProvider(
            self,
            f"user_pool_idp_google_{tag}",
            provider_name="Google",
            provider_type="Google",
            user_pool_id=user_pool.ref,
            provider_details={
                "client_id": self._secrets["google.app_id"],
                "client_secret": self._secrets["google.app_secret"],
                "authorize_scopes": self._secrets["google.scopes"],
            },
            attribute_mapping={"email": "email", "name": "name", "username": "sub"},
        )
        return [facebook_identity_provider, google_identity_provider]

    def create_user_pool_client(
            self,
            user_pool: aws_cognito.CfnUserPool,
            tag: str,
            federation_providers: List[aws_cognito.CfnUserPoolIdentityProvider]
    ) -> aws_cognito.CfnUserPoolClient:
        if not federation_providers:
            user_pool_client = aws_cognito.CfnUserPoolClient(
                self, f"userpool_client_{tag}", generate_secret=True, user_pool_id=user_pool.ref,
            )
            return user_pool_client

        user_pool_client = aws_cognito.CfnUserPoolClient(
            self,
            f"userpool_client_{tag}",
            generate_secret=True,
            user_pool_id=user_pool.ref,
            allowed_o_auth_flows=["code"],
            allowed_o_auth_flows_user_pool_client=True,
            allowed_o_auth_scopes=[
                "phone",
                "email",
                "openid",
                "profile",
                "aws.cognito.signin.user.admin",
            ],
            callback_ur_ls=[self._secrets["hostedui.sign_in_redirect"]],
            logout_ur_ls=[self._secrets["hostedui.sign_out_redirect"]],
            explicit_auth_flows=[
                "ALLOW_CUSTOM_AUTH",
                "ALLOW_USER_SRP_AUTH",
                "ALLOW_REFRESH_TOKEN_AUTH",
            ],
            prevent_user_existence_errors="LEGACY",
            supported_identity_providers=["COGNITO", "Facebook", "Google"],
        )

        # Ensure the federation provider dependency is explicit, so lets the provider setup complete
        # before attempting to create the user pool client.
        for provider in federation_providers:
            user_pool_client.node.add_dependency(provider)

        return user_pool_client

    def create_userpool_client_secret(
        self,
        user_pool: aws_cognito.CfnUserPool,
        user_pool_client: aws_cognito.CfnUserPoolClient,
        tag: str,
    ) -> custom_resources.AwsCustomResource:
        """
        :return: an AwsCustomResource that provides access to the user pool client secret in the
            response field `user_pool_client_secret`
        """
        resource = custom_resources.AwsCustomResource(
            self,
            f"userpool_client_secret_{tag}",
            resource_type="Custom::UserPoolClientSecret",
            policy=custom_resources.AwsCustomResourcePolicy.from_statements(
                [
                    aws_iam.PolicyStatement(
                        effect=aws_iam.Effect.ALLOW,
                        actions=["cognito-idp:DescribeUserPoolClient"],
                        resources=[
                            f"arn:aws:cognito-idp:{self.region}:{self.account}:userpool/{user_pool.ref}"  # noqa: E501
                        ],
                    )
                ]
            ),
            on_create=custom_resources.AwsSdkCall(
                physical_resource_id=custom_resources.PhysicalResourceId.of(user_pool_client.ref),
                service="CognitoIdentityServiceProvider",
                action="describeUserPoolClient",
                output_path="UserPoolClient.ClientSecret",
                parameters={"ClientId": user_pool_client.ref, "UserPoolId": user_pool.ref},
            ),
            on_update=custom_resources.AwsSdkCall(
                physical_resource_id=custom_resources.PhysicalResourceId.of(user_pool_client.ref),
                service="CognitoIdentityServiceProvider",
                action="describeUserPoolClient",
                output_path="UserPoolClient.ClientSecret",
                parameters={"ClientId": user_pool_client.ref, "UserPoolId": user_pool.ref},
            ),
        )
        return resource

    def create_user_pool_domain(self, user_pool: aws_cognito.CfnUserPool, tag: str):
        domain_prefix = self._secrets["hostedui.domain_prefix"]
        domain = aws_cognito.CfnUserPoolDomain(
            self, f"user_pool_domain_{tag}", domain=domain_prefix, user_pool_id=user_pool.ref,
        )
        return domain

    def create_custom_auth_lambda_configuration(
            self
    ) -> aws_cognito.CfnUserPool.LambdaConfigProperty:
        cognito_service_principal = aws_iam.ServicePrincipal("cognito-idp.amazonaws.com")
        create_auth_challenge = aws_lambda.Function(
            self,
            "custom_auth_lambda_create_auth_challenge",
            runtime=aws_lambda.Runtime.NODEJS_10_X,
            code=aws_lambda.Code.asset("custom_resources/custom_auth"),
            handler="create_auth_challenge.handler",
            description="custom auth: create_auth_challenge",
            current_version_options=aws_lambda.VersionOptions(
                removal_policy=core.RemovalPolicy.DESTROY
            ),
        )
        create_auth_challenge.add_permission(
            "create_auth_challenge_invoke_permission", principal=cognito_service_principal
        )

        define_auth_challenge = aws_lambda.Function(
            self,
            "custom_auth_lambda_define_auth_challenge",
            runtime=aws_lambda.Runtime.NODEJS_10_X,
            code=aws_lambda.Code.asset("custom_resources/custom_auth"),
            handler="define_auth_challenge.handler",
            description="custom auth: define_auth_challenge",
            current_version_options=aws_lambda.VersionOptions(
                removal_policy=core.RemovalPolicy.DESTROY
            ),
        )
        define_auth_challenge.add_permission(
            "define_auth_challenge_invoke_permission", principal=cognito_service_principal
        )

        pre_sign_up = aws_lambda.Function(
            self,
            "custom_auth_lambda_pre_sign_up",
            runtime=aws_lambda.Runtime.NODEJS_10_X,
            code=aws_lambda.Code.asset("custom_resources/custom_auth"),
            handler="pre_sign_up.handler",
            description="custom auth: pre_sign_up",
            current_version_options=aws_lambda.VersionOptions(
                removal_policy=core.RemovalPolicy.DESTROY
            ),
        )
        pre_sign_up.add_permission(
            "pre_sign_up_invoke_permission", principal=cognito_service_principal
        )

        verify_auth_challenge_response = aws_lambda.Function(
            self,
            "custom_auth_lambda_verify_auth_challenge_response",
            runtime=aws_lambda.Runtime.NODEJS_10_X,
            code=aws_lambda.Code.asset("custom_resources/custom_auth"),
            handler="verify_auth_challenge_response.handler",
            description="custom auth: verify_auth_challenge_response",
            current_version_options=aws_lambda.VersionOptions(
                removal_policy=core.RemovalPolicy.DESTROY
            ),
        )
        verify_auth_challenge_response.add_permission(
            "verify_auth_challenge_response_invoke_permission", principal=cognito_service_principal
        )

        return aws_cognito.CfnUserPool.LambdaConfigProperty(
            create_auth_challenge=create_auth_challenge.function_arn,
            define_auth_challenge=define_auth_challenge.function_arn,
            pre_sign_up=pre_sign_up.function_arn,
            verify_auth_challenge_response=verify_auth_challenge_response.function_arn,
        )

    def update_common_stack_with_test_policy(self, common_stack: CommonStack):
        stack_policy = aws_iam.PolicyStatement(
            effect=aws_iam.Effect.ALLOW, actions=["cognito-identity:*"], resources=["*"]
        )
        common_stack.add_to_common_role_policies(self, policy_to_add=stack_policy)

    def update_parameters_for_identity_pool(self, identity_pool: aws_cognito.CfnIdentityPool):
        self._parameters_to_save.update(
            {
                "developer_provider_name": MobileClientStack.DEVELOPER_PROVIDER_NAME,
                "awsconfiguration/CredentialsProvider/CognitoIdentity/Default/PoolId": identity_pool.ref,  # noqa: E501
                "awsconfiguration/CredentialsProvider/CognitoIdentity/Default/Region": self.region,
            }
        )

    def update_parameters_for_userpool(
        self,
        user_pool: aws_cognito.CfnUserPool,
        user_pool_client: aws_cognito.CfnUserPoolClient,
        user_pool_client_secret: custom_resources.AwsCustomResource,
        user_pool_domain: Optional[aws_cognito.CfnUserPoolDomain],
        tag: str,
    ):
        pool_id = user_pool.ref
        app_client_id = user_pool_client.ref
        app_client_secret = user_pool_client_secret.get_response_field(
            "UserPoolClient.ClientSecret"
        )
        self._parameters_to_save.update(
            {
                f"awsconfiguration/CognitoUserPool/{tag}/PoolId": pool_id,
                f"awsconfiguration/CognitoUserPool/{tag}/AppClientId": app_client_id,
                f"awsconfiguration/CognitoUserPool/{tag}/AppClientSecret": app_client_secret,
                f"awsconfiguration/CognitoUserPool/{tag}/Region": self.region,
            }
        )

        if user_pool_domain:
            url = f"https://{user_pool_domain.domain}.auth.{self.region}.amazoncognito.com"
            scopes_string = self._secrets["hostedui.scopes"]
            scopes = scopes_string.split()
            sign_in_uri = self._secrets["hostedui.sign_in_redirect"]
            sign_out_uri = self._secrets["hostedui.sign_out_redirect"]
            self._parameters_to_save.update(
                {
                    f"awsconfiguration/CognitoUserPool/{tag}/HostedUI/WebDomain": url,
                    f"awsconfiguration/CognitoUserPool/{tag}/HostedUI/AppClientId": app_client_id,
                    f"awsconfiguration/CognitoUserPool/{tag}/HostedUI/AppClientSecret": app_client_secret,  # noqa: E501
                    f"awsconfiguration/CognitoUserPool/{tag}/HostedUI/SignInRedirectURI": sign_in_uri,  # noqa: E501
                    f"awsconfiguration/CognitoUserPool/{tag}/HostedUI/SignOutRedirectURI": sign_out_uri,  # noqa: E501
                    f"awsconfiguration/CognitoUserPool/{tag}/HostedUI/Scopes": scopes,
                }
            )

    def update_parameters_for_s3_bucket(self, bucket: aws_s3.Bucket):
        self._parameters_to_save.update(
            {
                "awsconfiguration/S3TransferUtility/Default/Bucket": bucket.bucket_name,
                "awsconfiguration/S3TransferUtility/Default/Region": self.region,
            }
        )

    def update_parameters_for_auth_section(
        self,
        user_pool_client: aws_cognito.CfnUserPoolClient,
        user_pool_client_secret: custom_resources.AwsCustomResource,
        user_pool_domain: Optional[aws_cognito.CfnUserPoolDomain],
        tag: str,
    ):
        """
        This contains nearly identical info as the "HostedUI" section above, but
        is organized differently for the AWSMobileClient.
        """
        if not user_pool_domain:
            return

        app_client_id = user_pool_client.ref
        app_client_secret = user_pool_client_secret.get_response_field(
            "UserPoolClient.ClientSecret"
        )

        web_domain = f"{user_pool_domain.domain}.auth.{self.region}.amazoncognito.com"
        scopes_string = self._secrets["hostedui.scopes"]
        scopes = scopes_string.split()
        sign_in_uri = self._secrets["hostedui.sign_in_redirect"]
        sign_out_uri = self._secrets["hostedui.sign_out_redirect"]
        self._parameters_to_save.update(
            {
                f"awsconfiguration/Auth/{tag}/OAuth/WebDomain": web_domain,
                f"awsconfiguration/Auth/{tag}/OAuth/AppClientId": app_client_id,
                f"awsconfiguration/Auth/{tag}/OAuth/AppClientSecret": app_client_secret,
                f"awsconfiguration/Auth/{tag}/OAuth/SignInRedirectURI": sign_in_uri,
                f"awsconfiguration/Auth/{tag}/OAuth/SignOutRedirectURI": sign_out_uri,
                f"awsconfiguration/Auth/{tag}/OAuth/Scopes": scopes,
            }
        )

    @staticmethod
    def add_public_policy(bucket: aws_s3.Bucket, role: aws_iam.Role, is_auth_role: bool):
        actions = ["s3:GetObject"]
        if is_auth_role:
            actions.extend(["s3:PutObject", "s3:DeleteObject"])
        policy = aws_iam.PolicyStatement(
            effect=aws_iam.Effect.ALLOW,
            actions=actions,
            resources=[f"arn:aws:s3:::{bucket.bucket_name}/public/*"],
        )
        role.add_to_policy(policy)

    @staticmethod
    def add_read_policy(bucket: aws_s3.Bucket, role: aws_iam.Role):
        policy = aws_iam.PolicyStatement(
            effect=aws_iam.Effect.ALLOW,
            actions=["s3:GetObject"],
            resources=[f"arn:aws:s3:::{bucket.bucket_name}/protected/*"],
        )
        role.add_to_policy(policy)

    @staticmethod
    def add_list_policy(bucket: aws_s3.Bucket, role: aws_iam.Role, is_auth_role: bool):
        policy = aws_iam.PolicyStatement(
            effect=aws_iam.Effect.ALLOW,
            actions=["s3:ListBucket"],
            resources=[f"arn:aws:s3:::{bucket.bucket_name}"],
        )

        prefixes = ["public/", "public/*", "protected/", "protected/*"]
        if is_auth_role:
            prefixes.extend(
                [
                    "private/${cognito-identity.amazonaws.com:sub}/",
                    "private/${cognito-identity.amazonaws.com:sub}/*",
                ]
            )
        policy.add_conditions({"StringLike": {"s3:prefix": prefixes}})
        role.add_to_policy(policy)

    @staticmethod
    def add_user_specific_policy(bucket: aws_s3.Bucket, role: aws_iam.Role, prefix: str):
        policy = aws_iam.PolicyStatement(
            effect=aws_iam.Effect.ALLOW,
            actions=["s3:GetObject", "s3:PutObject", "s3:DeleteObject"],
            resources=[
                f"arn:aws:s3:::{bucket.bucket_name}/{prefix}/${{cognito-identity.amazonaws.com:sub}}/*"  # noqa: E501
            ],
        )
        role.add_to_policy(policy)

    @staticmethod
    def add_uploads_policy(bucket: aws_s3.Bucket, role: aws_iam.Role):
        policy = aws_iam.PolicyStatement(
            effect=aws_iam.Effect.ALLOW,
            actions=["s3:PutObject"],
            resources=[f"arn:aws:s3:::{bucket.bucket_name}/uploads/*"],
        )
        role.add_to_policy(policy)
