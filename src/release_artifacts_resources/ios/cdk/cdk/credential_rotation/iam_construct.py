from aws_cdk import aws_iam, core


class IAMConstruct(core.Construct):
    def __init__(
        self,
        scope: core.Construct,
        construct_id: str,
        bucket_arn: str,
        cloudfront_arn: str,
        **kwargs
    ) -> None:

        super().__init__(scope, construct_id, **kwargs)
        self.create_circleci_release_user()
        self.create_circleci_release_proceess_role(bucket_arn=bucket_arn, cloudfront_arn=cloudfront_arn)
        self.create_lambda_execution_role()

    def create_circleci_release_user(self) -> None:
        self.circleci_user = aws_iam.User(self, "circleci_iam_user", user_name="CircleCIReleaseProcessIAMUser")

    def create_circleci_release_proceess_role(self, bucket_arn: str, cloudfront_arn: str) -> None:
        self.circleci_release_role = aws_iam.Role(
            self,
            "circleci_release_role",
            assumed_by=self.circleci_user,
            role_name="CircleCIReleaseProcessRole",
            max_session_duration=core.Duration.hours(4),
        )

        bucket_policy = aws_iam.PolicyStatement(
            effect=aws_iam.Effect.ALLOW,
            actions=["s3:PutObject"],
            resources=[bucket_arn],
        )
        self.circleci_release_role.add_to_policy(bucket_policy)

        cloudfront_policy = aws_iam.PolicyStatement(
            effect=aws_iam.Effect.ALLOW,
            actions=["cloudfront:CreateInvalidation"],
            resources=[cloudfront_arn],
        )
        self.circleci_release_role.add_to_policy(cloudfront_policy)

    def create_lambda_execution_role(self) -> None:
        self.lambda_role = aws_iam.Role(
            self,
            "lambda_key_rotation_execution_role",
            assumed_by=aws_iam.ServicePrincipal("lambda.amazonaws.com"),
            role_name="LambdaKeyRotationExecutionRole",
        )
        self.lambda_role.add_managed_policy(
            aws_iam.ManagedPolicy.from_aws_managed_policy_name(
                "service-role/AWSLambdaBasicExecutionRole"
            )
        )

        logs_policy = aws_iam.PolicyStatement(
             effect=aws_iam.Effect.ALLOW, actions=["cloudwatch:*", "logs:*"], resources=["*"]
         )
        self.lambda_role.add_to_policy(logs_policy)

        lambda_role_rotate_keys_policy = aws_iam.PolicyStatement(
            effect=aws_iam.Effect.ALLOW,
            actions=["iam:CreateAccessKey", "iam:DeleteAccessKey"],
            resources=[self.circleci_user.user_arn],
        )
        self.lambda_role.add_to_policy(lambda_role_rotate_keys_policy)

    def add_policy_to_lambda_role(self, policy: aws_iam.PolicyStatement) -> None:
        self.lambda_role.add_to_policy(policy)
