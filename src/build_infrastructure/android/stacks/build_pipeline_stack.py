import boto3
import base64
from ruamel import yaml
import json
import os
from typing import cast
from botocore.exceptions import ClientError
from aws_cdk import (
    core,
    custom_resources,
    aws_iam,
    aws_codebuild,
    aws_codepipeline,
    aws_codepipeline_actions,
    aws_cloudformation,
    aws_lambda,
    aws_logs,
    aws_s3
)
from amplify_custom_resources import DeviceFarmProject
from amplify_custom_resources import PullRequestBuilder
class AmplifyAndroidCodePipeline(core.Stack):
    CODE_BUILD_AMPLIFY_ACTIONS = [
        "amplify:CreateApp",
        "amplify:CreateBackendEnvironment",
        "amplify:CreateBranch",
        "amplify:DeleteApp",
        "amplify:DeleteBackendEnvironment",
        "amplify:DeleteBranch",
        "amplify:GetApp",
        "amplify:GetBackendEnvironment",
        "amplify:ListApps",
        "amplify:ListBackendEnvironments",
        "amplify:ListBranches",
        "amplify:ListDomainAssociations",
        "amplify:UpdateApp",
        "apigateway:DELETE",
        "apigateway:GET",
        "apigateway:PATCH",
        "apigateway:POST",
        "apigateway:PUT",
        "appsync:CreateApiKey",
        "appsync:CreateDataSource",
        "appsync:CreateFunction",
        "appsync:CreateGraphqlApi",
        "appsync:CreateResolver",
        "appsync:CreateType",
        "appsync:DeleteApiKey",
        "appsync:DeleteDataSource",
        "appsync:DeleteFunction",
        "appsync:DeleteGraphqlApi",
        "appsync:DeleteResolver",
        "appsync:DeleteType",
        "appsync:GetDataSource",
        "appsync:GetFunction",
        "appsync:GetGraphqlApi",
        "appsync:GetIntrospectionSchema",
        "appsync:GetResolver",
        "appsync:GetSchemaCreationStatus",
        "appsync:GetType",
        "appsync:GraphQL",
        "appsync:ListApiKeys",
        "appsync:ListDataSources",
        "appsync:ListFunctions",
        "appsync:ListGraphqlApis",
        "appsync:ListResolvers",
        "appsync:ListResolversByFunction",
        "appsync:ListTagsForResource",
        "appsync:ListTypes",
        "appsync:StartSchemaCreation",
        "appsync:TagResource",
        "appsync:UpdateApiKey",
        "appsync:UpdateDataSource",
        "appsync:UpdateFunction",
        "appsync:UpdateGraphqlApi",
        "appsync:UpdateResolver",
        "appsync:UpdateType",
        "cloudformation:CreateChangeSet",
        "cloudformation:CreateStack",
        "cloudformation:CreateStackSet",
        "cloudformation:DeleteStack",
        "cloudformation:DeleteStackSet",
        "cloudformation:DescribeChangeSet",
        "cloudformation:DescribeStackEvents",
        "cloudformation:DescribeStackResource",
        "cloudformation:DescribeStackResources",
        "cloudformation:DescribeStackSet",
        "cloudformation:DescribeStackSetOperation",
        "cloudformation:DescribeStacks",
        "cloudformation:ExecuteChangeSet",
        "cloudformation:GetTemplate",
        "cloudformation:UpdateStack",
        "cloudformation:UpdateStackSet",
        "cloudfront:CreateCloudFrontOriginAccessIdentity",
        "cloudfront:CreateDistribution",
        "cloudfront:DeleteCloudFrontOriginAccessIdentity",
        "cloudfront:DeleteDistribution",
        "cloudfront:GetCloudFrontOriginAccessIdentity",
        "cloudfront:GetCloudFrontOriginAccessIdentityConfig",
        "cloudfront:GetDistribution",
        "cloudfront:GetDistributionConfig",
        "cloudfront:TagResource",
        "cloudfront:UntagResource",
        "cloudfront:UpdateCloudFrontOriginAccessIdentity",
        "cloudfront:UpdateDistribution",
        "cognito-identity:CreateIdentityPool",
        "cognito-identity:DeleteIdentityPool",
        "cognito-identity:DescribeIdentity",
        "cognito-identity:DescribeIdentityPool",
        "cognito-identity:SetIdentityPoolRoles",
        "cognito-identity:GetIdentityPoolRoles",
        "cognito-identity:TagResource",
        "cognito-identity:UpdateIdentityPool",
        "cognito-idp:AdminAddUserToGroup",
        "cognito-idp:AdminCreateUser",
        "cognito-idp:CreateGroup",
        "cognito-idp:CreateUserPool",
        "cognito-idp:CreateUserPoolClient",
        "cognito-idp:DeleteGroup",
        "cognito-idp:DeleteUser",
        "cognito-idp:DeleteUserPool",
        "cognito-idp:DeleteUserPoolClient",
        "cognito-idp:DescribeUserPool",
        "cognito-idp:DescribeUserPoolClient",
        "cognito-idp:ListTagsForResource",
        "cognito-idp:ListUserPoolClients",
        "cognito-idp:UpdateUserPool",
        "cognito-idp:UpdateUserPoolClient",
        "dynamodb:CreateTable",
        "dynamodb:DeleteItem",
        "dynamodb:DeleteTable",
        "dynamodb:DescribeContinuousBackups",
        "dynamodb:DescribeTable",
        "dynamodb:DescribeTimeToLive",
        "dynamodb:ListStreams",
        "dynamodb:PutItem",
        "dynamodb:TagResource",
        "dynamodb:UpdateContinuousBackups",
        "dynamodb:UpdateItem",
        "dynamodb:UpdateTable",
        "dynamodb:UpdateTimeToLive",
        "es:AddTags",
        "es:CreateElasticsearchDomain",
        "es:DeleteElasticsearchDomain",
        "es:DescribeElasticsearchDomain",
        "events:DeleteRule",
        "events:DescribeRule",
        "events:ListRuleNamesByTarget",
        "events:PutRule",
        "events:PutTargets",
        "events:RemoveTargets",
        "iam:AttachRolePolicy",
        "iam:CreatePolicy",
        "iam:CreateRole",
        "iam:DeletePolicy",
        "iam:DeleteRole",
        "iam:DeleteRolePolicy",
        "iam:DetachRolePolicy",
        "iam:GetPolicy",
        "iam:GetRole",
        "iam:GetRolePolicy",
        "iam:GetUser",
        "iam:ListPolicyVersions",
        "iam:PassRole",
        "iam:PutRolePolicy",
        "iam:UpdateRole",
        "kinesis:AddTagsToStream",
        "kinesis:CreateStream",
        "kinesis:DeleteStream",
        "kinesis:DescribeStream",
        "kinesis:PutRecords",
        "lambda:AddLayerVersionPermission",
        "lambda:AddPermission",
        "lambda:CreateEventSourceMapping",
        "lambda:CreateFunction",
        "lambda:DeleteEventSourceMapping",
        "lambda:DeleteFunction",
        "lambda:DeleteLayerVersion",
        "lambda:GetEventSourceMapping",
        "lambda:GetFunction",
        "lambda:GetFunctionConfiguration",
        "lambda:GetLayerVersion",
        "lambda:GetLayerVersionByArn",
        "lambda:InvokeAsync",
        "lambda:InvokeFunction",
        "lambda:ListEventSourceMappings",
        "lambda:ListLayerVersions",
        "lambda:PublishLayerVersion",
        "lambda:RemoveLayerVersionPermission",
        "lambda:RemovePermission",
        "lambda:UpdateFunctionCode",
        "lambda:UpdateFunctionConfiguration",
        "lex:GetBot",
        "lex:GetBuiltinIntent",
        "lex:GetBuiltinIntents",
        "lex:GetBuiltinSlotTypes",
        "logs:DescribeLogStreams",
        "logs:GetLogEvents",
        "mobiletargeting:GetApp",
        "rekognition:DescribeCollection",
        "s3:CreateBucket",
        "s3:DeleteBucket",
        "s3:DeleteBucketPolicy",
        "s3:DeleteBucketWebsite",
        "s3:DeleteObject",
        "s3:GetBucketLocation",
        "s3:GetObject",
        "s3:HeadBucket",
        "s3:ListAllMyBuckets",
        "s3:ListBucket",
        "s3:PutBucketAcl",
        "s3:PutBucketCORS",
        "s3:PutBucketNotification",
        "s3:PutBucketPolicy",
        "s3:PutBucketWebsite",
        "s3:PutObject",
        "s3:PutObjectAcl"
    ]
    DEVICE_FARM_TEST_RUNNER_ACTIONS = [
            "devicefarm:List*",
            "devicefarm:Get*",
            "devicefarm:ScheduleRun",
            "devicefarm:DeleteRun",
            "devicefarm:StopRun",
            "devicefarm:CreateUpload",
            "devicefarm:UpdateUpload",
            "devicefarm:DeleteUpload"
        ]
    MODULES_WITH_INSTRUMENTED_TESTS = ['core', 'aws-analytics-pinpoint', 'aws-datastore', 'aws-api', 'aws-storage-s3', 'aws-predictions']
    code_build_project=None

    def __init__(self, scope: core.App, id: str, props, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        required_props = ['build_pipeline_name','github_source', 'config_source_bucket', 'device_farm_project_name', 'device_farm_pool_arn']
        for prop in required_props:
            if prop not in props:
                raise RuntimeError(f"Parameter {prop} is required.")
        
        github_source = cast(aws_codepipeline_actions.GitHubSourceAction, props['github_source'])
        config_source_bucket = props['config_source_bucket']
        device_farm_pool_arn = props['device_farm_pool_arn']
        device_farm_project_name = props['device_farm_project_name']
        build_pipeline_name = props['build_pipeline_name']
        codebuild_project_name_prefix = props['codebuild_project_name_prefix']

        df_project = DeviceFarmProject(self, id, project_name=device_farm_project_name)

        PullRequestBuilder(self, "UnitTestRunner", project_name=f"{codebuild_project_name_prefix}-UnitTest",github_owner=github_source.owner, github_repo=github_source.repo, buildspec_path="scripts/pr-builder-buildspec.yml")
        integtest_project = PullRequestBuilder(self, "IntegrationTestrunner", project_name=f"{codebuild_project_name_prefix}-IntegrationTest",github_owner=github_source.owner, 
                                                github_repo=github_source.repo, buildspec_path="scripts/devicefarm-test-runner-buildspec.yml", 
                                                environment_variables={
                                                    'DEVICEFARM_PROJECT_ARN': aws_codebuild.BuildEnvironmentVariable(value=df_project.get_arn()), 
                                                    'DEVICEFARM_POOL_ARN': aws_codebuild.BuildEnvironmentVariable(value=device_farm_pool_arn),
                                                    'CONFIG_SOURCE_BUCKET': aws_codebuild.BuildEnvironmentVariable(value=config_source_bucket)})
        self._add_codebuild_project_runner_permissions(integtest_project.role)
        self._add_devicefarm_test_runner_permissions_to_role(integtest_project.role)
    
    def get_codebuild_project_name(self):
        return self.code_build_project.project_name

    def _add_devicefarm_test_runner_permissions_to_role(self, role: aws_iam.Role):
        df_runner_policy = aws_iam.ManagedPolicy(self,
            "AmplifyAndroidDeviceFarmTestRunnerPolicy",
            managed_policy_name=f"AmplifyAndroidDeviceFarmTestRunnerPolicy",
            description="Policy used by the CodePipeline to trigger DeviceFarm test runs.",
            statements=[
                aws_iam.PolicyStatement(actions=self.DEVICE_FARM_TEST_RUNNER_ACTIONS, effect=aws_iam.Effect.ALLOW, resources=["*"]),
            ]
        )
        df_runner_policy.attach_to_role(role)

    def _add_devicefarm_test_stage(self, pipeline, device_farm_project_id, device_farm_pool_arn):
        test_actions = []
        for module_name in self.MODULES_WITH_INSTRUMENTED_TESTS:
            test_actions.append(self._create_devicefarm_test_action(device_farm_project_id, device_farm_pool_arn, module_name))

        testing_stage = {
            "Name": "Test",
            "Actions": test_actions
        }
        pipeline_node = pipeline.node.default_child
        pipeline_node.add_property_override("Stages.2", testing_stage)

    def _create_artifact_bucket(self, bucket_name:str):
        artifact_bucket = aws_s3.Bucket(self, "PipelineAssets", 
            bucket_name=bucket_name, 
            encryption=aws_s3.BucketEncryption.KMS_MANAGED,
            removal_policy=core.RemovalPolicy.DESTROY)
        artifact_bucket.add_to_resource_policy(permission=aws_iam.PolicyStatement(
            principals=[aws_iam.AnyPrincipal()],
            effect=aws_iam.Effect.DENY,
            resources=[
                artifact_bucket.bucket_arn, 
                f"{artifact_bucket.bucket_arn}/*"
            ],
            actions=["s3:*"],
            conditions={
                "Bool": {
                    "aws:SecureTransport": "false"
                }
            }
        ))
        artifact_bucket.add_to_resource_policy(permission=aws_iam.PolicyStatement(
            principals=[aws_iam.AnyPrincipal()],
            effect=aws_iam.Effect.DENY,
            resources=[
                artifact_bucket.bucket_arn, 
                f"{artifact_bucket.bucket_arn}/*"
            ],
            actions=["s3:PutObject"],
            conditions={
                "StringNotEquals": {
                    "s3:x-amz-server-side-encryption": "aws:kms"
                }
            }
        ))
        return artifact_bucket

    # Not calling this right now since we can't filter out PRs in CodePipeline.
    def _create_pipeline(self, 
                            build_pipeline_name: str, 
                            github_source: aws_codepipeline_actions.GitHubSourceAction, 
                            codebuild_project: aws_codebuild.PipelineProject,
                            config_file_source_bucket_name:str,
                            df_project: DeviceFarmProject,
                            device_farm_pool_arn:str):
        artifact_bucket = self._create_artifact_bucket(f"pipeline-assets-{build_pipeline_name.lower()}-{self.account}")
        self.code_build_project = self._create_codebuild_project("AmplifyAndroidCodeBuildProject")
        amplify_android_build_output = aws_codepipeline.Artifact("AmplifyAndroidBuildOutput")
        pipeline = aws_codepipeline.Pipeline(self, 
            f"{build_pipeline_name}Pipeline",
            pipeline_name=build_pipeline_name,
            artifact_bucket=artifact_bucket,
            stages=[
                aws_codepipeline.StageProps(
                    stage_name="Source",
                    actions=[ github_source ]
                ),
                aws_codepipeline.StageProps(
                    stage_name="Build",
                        actions=[self._create_build_and_assemble_action(input_artifact=github_source.action_properties.outputs[0],
                                                                            output_artifact=amplify_android_build_output, 
                                                                            pipeline_project=codebuild_project,
                                                                            config_source_bucket=config_file_source_bucket_name)
                                ]
                )
            ])
        self._add_devicefarm_test_runner_permissions_to_role(pipeline.role)
        self._add_devicefarm_test_stage(pipeline, df_project.get_project_id(), device_farm_pool_arn)
        return pipeline

    def _create_codebuild_project(self, id: str):
        pipeline_project = aws_codebuild.PipelineProject(self, 
                                            id, 
                                            environment=aws_codebuild.BuildEnvironment(build_image=aws_codebuild.LinuxBuildImage.AMAZON_LINUX_2_3, 
                                                                                        privileged=True,
                                                                                        compute_type=aws_codebuild.ComputeType.LARGE),
                                            build_spec=aws_codebuild.BuildSpec.from_source_filename(filename='scripts/apk-builder-buildspec.yml'))
        build_exec_policy = aws_iam.ManagedPolicy(self,
            "AmplifyAndroidBuildExecutorPolicy",
            managed_policy_name=f"AmplifyAndroidBuildExecutorPolicy",
            description="Policy used by the CodeBuild role that executes builds.",
            statements=[
                aws_iam.PolicyStatement(actions=self.CODE_BUILD_AMPLIFY_ACTIONS, effect=aws_iam.Effect.ALLOW, resources=["*"]),
            ]
        )
        build_exec_policy.attach_to_role(pipeline_project.role)
        return pipeline_project

    def _add_codebuild_project_runner_permissions(self, role: aws_iam.Role):
        build_exec_policy = aws_iam.ManagedPolicy(self,
            "AmplifyAndroidBuildExecutorPolicy",
            managed_policy_name=f"AmplifyAndroidBuildExecutorPolicy",
            description="Policy used by the CodeBuild role that executes builds.",
            statements=[
                aws_iam.PolicyStatement(actions=self.CODE_BUILD_AMPLIFY_ACTIONS, effect=aws_iam.Effect.ALLOW, resources=["*"]),
            ]
        )
        build_exec_policy.attach_to_role(role)


    def _create_build_and_assemble_action(self,
        input_artifact:aws_codepipeline.Artifact,
        output_artifact:aws_codepipeline.Artifact, 
        pipeline_project:aws_codebuild.PipelineProject,
        config_source_bucket: str = None):
        if config_source_bucket is None:
            return aws_codepipeline_actions.CodeBuildAction(
                action_name='BuildAndAssemble',
                input=input_artifact,
                project=pipeline_project,
                outputs=[output_artifact]
            )
        else:
            return aws_codepipeline_actions.CodeBuildAction(
                action_name='BuildAndAssemble',
                input=input_artifact,
                project=pipeline_project,
                environment_variables={
                    'CONFIG_SOURCE_BUCKET': aws_codebuild.BuildEnvironmentVariable(value=config_source_bucket)
                },
                outputs=[output_artifact]
            )

    def _create_devicefarm_test_action(self, project_id: str, device_pool_arn: str, module_name: str):
        return {
            "Name":f"{module_name}-InstrumentedTests",
            "ActionTypeId": {
                "Category": "Test",
                "Owner": "AWS",
                "Provider": "DeviceFarm",
                "Version": "1"
            },
            "RunOrder": 1,
            "Configuration": {
                "App": f"{module_name}-debug-androidTest.apk",
                "Test": f"{module_name}-debug-androidTest.apk",
                "AppType": "Android",
                "DevicePoolArn": device_pool_arn,
                "ProjectId": project_id,
                "TestType": "INSTRUMENTATION"
            },
            "OutputArtifacts": [],
            "InputArtifacts": [
                {
                    "Name": "AmplifyAndroidBuildOutput"
                }
            ]
        }
