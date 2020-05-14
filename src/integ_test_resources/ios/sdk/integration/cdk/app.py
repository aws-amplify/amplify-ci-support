#!/usr/bin/env python3

from aws_cdk import core

from cdk_integration_tests_ios.apigateway_stack import ApigatewayStack
from cdk_integration_tests_ios.autoscaling_stack import AutoScalingStack
from cdk_integration_tests_ios.cloudwatch_stack import CloudWatchStack
from cdk_integration_tests_ios.cognito_idp_stack import CognitoIdpStack
from cdk_integration_tests_ios.comprehend_stack import ComprehendStack
from cdk_integration_tests_ios.core_stack import CoreStack
from cdk_integration_tests_ios.dynamodb_stack import DynamoDbStack
from cdk_integration_tests_ios.ec2_stack import Ec2Stack
from cdk_integration_tests_ios.elb_stack import ElbStack
from cdk_integration_tests_ios.firehose_stack import FirehoseStack
from cdk_integration_tests_ios.iot_stack import IotStack
from cdk_integration_tests_ios.kinesis_stack import KinesisStack
from cdk_integration_tests_ios.kinesisvideo_stack import KinesisVideoStack
from cdk_integration_tests_ios.kms_stack import KmsStack
from cdk_integration_tests_ios.lambda_stack import LambdaStack
from cdk_integration_tests_ios.mobileclient_stack import MobileClientStack
from cdk_integration_tests_ios.pinpoint_stack import PinpointStack
from cdk_integration_tests_ios.polly_stack import PollyStack
from cdk_integration_tests_ios.rekognition_stack import RekognitionStack
from cdk_integration_tests_ios.s3_stack import S3Stack
from cdk_integration_tests_ios.ses_stack import SesStack
from cdk_integration_tests_ios.simpledb_stack import SimpleDbStack
from cdk_integration_tests_ios.sns_stack import SnsStack
from cdk_integration_tests_ios.sqs_stack import SqsStack
from cdk_integration_tests_ios.sts_stack import StsStack
from cdk_integration_tests_ios.textract_stack import TextractStack
from cdk_integration_tests_ios.transcribe_stack import TranscribeStack
from cdk_integration_tests_ios.translate_stack import TranslateStack
from common.common_stack import CommonStack
from common.main_stack import MainStack
from common.platforms import Platform
from common.stack_utils import add_stack_dependency_on_common_stack

app = core.App()

region = app.node.try_get_context("region")
account = app.node.try_get_context("account")
if region is None or account is None:
    raise ValueError(
        "Provide region and account in 'context' parameter, as in: cdk deploy app -c region=us-west-2 -c account=123456"  # noqa: E501
    )

common_stack = CommonStack(app, "common", platform=Platform.IOS)
main_stack = MainStack(app, "main")
main_stack.add_dependency(common_stack)

core_stack = CoreStack(app, "core", common_stack)

lambda_stack = LambdaStack(app, "lambda", common_stack)

stacks_in_app = [
    core_stack,
    lambda_stack,
    ApigatewayStack(app, "apigateway", lambda_stack.lambda_echo_function, common_stack),
    AutoScalingStack(app, "autoscaling", common_stack),
    CloudWatchStack(app, "cloudwatch", common_stack),
    CognitoIdpStack(app, "cognito-idp", common_stack),
    ComprehendStack(app, "comprehend", common_stack),
    DynamoDbStack(app, "dynamodb", common_stack),
    Ec2Stack(app, "ec2", common_stack),
    ElbStack(app, "elb", common_stack),
    FirehoseStack(app, "firehose", common_stack),
    IotStack(app, "iot", common_stack),
    KinesisStack(app, "kinesis", common_stack),
    KinesisVideoStack(app, "kinesisvideo", common_stack),
    KmsStack(app, "kms", common_stack),
    MobileClientStack(app, "mobileclient", common_stack),
    PinpointStack(app, "pinpoint", common_stack),
    PollyStack(app, "polly", common_stack),
    RekognitionStack(app, "rekognition", common_stack),
    S3Stack(app, "s3", common_stack),
    SesStack(app, "ses", common_stack),
    SimpleDbStack(app, "sdb", common_stack),
    SnsStack(app, "sns", common_stack),
    SqsStack(app, "sqs", common_stack),
    StsStack(app, "sts", common_stack),
    TextractStack(app, "textract", common_stack),
    TranscribeStack(app, "transcribe", common_stack),
    TranslateStack(app, "translate", common_stack),
]

add_stack_dependency_on_common_stack(stacks_in_app=stacks_in_app, common_stack=common_stack)
main_stack.add_dependencies_with_region_filter(stacks_to_add=stacks_in_app)

app.synth()
