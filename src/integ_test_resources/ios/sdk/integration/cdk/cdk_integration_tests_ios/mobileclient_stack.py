from aws_cdk import aws_cognito, aws_iam, aws_s3, core, custom_resources

from common.auth_utils import construct_identity_pool
from common.common_stack import CommonStack
from common.platforms import Platform
from common.region_aware_stack import RegionAwareStack


class MobileClientStack(RegionAwareStack):
    def __init__(self, scope: core.Construct, id: str, common_stack: CommonStack, **kwargs) -> None:

        super().__init__(scope, id, **kwargs)

        self._parameters_to_save["email_address"] = "aws-mobile-sdk-dev+mc-integ-tests@amazon.com"

        self._supported_in_region = self.are_services_supported_in_region(
            ["cognito-identity", "cognito-idp"]
        )

        self.update_common_stack_with_test_policy(common_stack)

        default_user_pool = self.create_user_pool("default")
        default_user_pool_client = self.create_user_pool_client(default_user_pool, "default")
        default_user_pool_client_secret = self.create_userpool_client_secret(
            default_user_pool, default_user_pool_client, "default"
        )
        self.update_parameters_for_userpool(
            default_user_pool, default_user_pool_client, default_user_pool_client_secret, "Default"
        )

        (identity_pool, auth_role, unauth_role) = construct_identity_pool(
            self,
            resource_id_prefix="mobileclient",
            cognito_identity_providers=[
                {
                    "clientId": default_user_pool_client.ref,
                    "providerName": f"cognito-idp.{self.region}.amazonaws.com/{default_user_pool.ref}",
                }
            ],
        )
        self.update_parameters_for_identity_pool(identity_pool)

        custom_auth_user_pool = self.create_user_pool("custom_auth")
        custom_auth_user_pool_client = self.create_user_pool_client(
            custom_auth_user_pool, "custom_auth"
        )
        custom_auth_user_pool_client_secret = self.create_userpool_client_secret(
            custom_auth_user_pool, custom_auth_user_pool_client, "custom_auth"
        )
        self.update_parameters_for_userpool(
            custom_auth_user_pool,
            custom_auth_user_pool_client,
            custom_auth_user_pool_client_secret,
            "DefaultCustomAuth",
        )

        s3_bucket = self.create_s3_bucket_and_policies(auth_role, unauth_role)
        self.update_parameters_for_s3_bucket(s3_bucket)

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
        bucket = aws_s3.Bucket(self, "integ_test_mobileclient_bucket")
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

    def create_user_pool(self, tag) -> aws_cognito.UserPool:
        user_pool = aws_cognito.CfnUserPool(
            self,
            f"userpool_{tag}",
            auto_verified_attributes=["email"],
            device_configuration=aws_cognito.CfnUserPool.DeviceConfigurationProperty(
                challenge_required_on_new_device=False,
                device_only_remembered_on_user_prompt=True
            ),
            schema=[
                aws_cognito.CfnUserPool.SchemaAttributeProperty(
                    attribute_data_type="String",
                    mutable=False,
                    name="email",
                    required=True,
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
                )
            ],
        )
        return user_pool

    def create_user_pool_client(self, user_pool, tag) -> aws_cognito.CfnUserPoolClient:
        user_pool_client = aws_cognito.CfnUserPoolClient(
            self,
            f"userpool_client_{tag}",
            generate_secret=True,
            user_pool_id=user_pool.ref,
        )
        return user_pool_client

    def create_userpool_client_secret(
        self, user_pool, user_pool_client, tag
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

    def update_common_stack_with_test_policy(self, common_stack):
        stack_policy = aws_iam.PolicyStatement(
            effect=aws_iam.Effect.ALLOW, actions=["cognito-identity:*"], resources=["*"]
        )
        common_stack.add_to_common_role_policies(self, policy_to_add=stack_policy)

    def update_parameters_for_identity_pool(self, identity_pool):
        self._parameters_to_save.update(
            {
                "awsconfiguration/CredentialsProvider/CognitoIdentity/Default/PoolId": identity_pool.ref,  # noqa: E501
                "awsconfiguration/CredentialsProvider/CognitoIdentity/Default/Region": self.region,
            }
        )

    def update_parameters_for_userpool(
        self, user_pool, user_pool_client, user_pool_client_secret, tag
    ):
        self._parameters_to_save.update(
            {
                f"awsconfiguration/CognitoUserPool/{tag}/PoolId": user_pool.ref,
                f"awsconfiguration/CognitoUserPool/{tag}/AppClientId": user_pool_client.ref,
                f"awsconfiguration/CognitoUserPool/{tag}/AppClientSecret": user_pool_client_secret.get_response_field(  # noqa: E501
                    "UserPoolClient.ClientSecret"
                ),
                f"awsconfiguration/CognitoUserPool/{tag}/Region": self.region,
            }
        )

    def update_parameters_for_s3_bucket(self, bucket):
        self._parameters_to_save.update(
            {
                "awsconfiguration/S3TransferUtility/Default/Bucket": bucket.bucket_name,
                "awsconfiguration/S3TransferUtility/Default/Region": self.region,
            }
        )

    @staticmethod
    def add_public_policy(bucket, role: aws_iam.Role, is_auth_role):
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
    def add_read_policy(bucket, role: aws_iam.Role):
        policy = aws_iam.PolicyStatement(
            effect=aws_iam.Effect.ALLOW,
            actions=["s3:GetObject"],
            resources=[f"arn:aws:s3:::{bucket.bucket_name}/protected/*"],
        )
        role.add_to_policy(policy)

    @staticmethod
    def add_list_policy(bucket, role: aws_iam.Role, is_auth_role):
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
    def add_user_specific_policy(bucket, role: aws_iam.Role, prefix):
        policy = aws_iam.PolicyStatement(
            effect=aws_iam.Effect.ALLOW,
            actions=["s3:GetObject", "s3:PutObject", "s3:DeleteObject"],
            resources=[
                f"arn:aws:s3:::{bucket.bucket_name}/{prefix}/${{cognito-identity.amazonaws.com:sub}}/*"  # noqa: E501
            ],
        )
        role.add_to_policy(policy)

    @staticmethod
    def add_uploads_policy(bucket, role: aws_iam.Role):
        policy = aws_iam.PolicyStatement(
            effect=aws_iam.Effect.ALLOW,
            actions=["s3:PutObject"],
            resources=[f"arn:aws:s3:::{bucket.bucket_name}/uploads/*"],
        )
        role.add_to_policy(policy)
