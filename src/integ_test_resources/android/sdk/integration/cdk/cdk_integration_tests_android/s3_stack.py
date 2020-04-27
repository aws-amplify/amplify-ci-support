from aws_cdk import aws_iam as iam
from aws_cdk import aws_kms as kms
from aws_cdk import aws_s3 as s3
from aws_cdk import core

import sys
import os
sys.path.append(
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)), '../../../../..'))
from common.parameters import string_parameter


class S3Stack(core.Stack):

    def __init__(self,
                 scope: core.Construct,
                 id: str,
                 circleci_execution_role: iam.Role,
                 **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Create policy for KMS key
        policy = iam.PolicyDocument(
            statements=[
                iam.PolicyStatement(
                    actions=['kms:*'],
                    effect=iam.Effect.ALLOW,
                    resources=['*'],
                    principals=[iam.AccountPrincipal(core.Aws.ACCOUNT_ID)]
                )
            ]
        )

        # Create KMS key for S3 server-side encryption
        key = kms.Key(self, 's3SSETestkmsKey', policy=policy)

        # Create S3 bucket for SSE testing
        bucket = s3.Bucket(
            self, 's3TestBucket',
            encryption=s3.BucketEncryption.KMS,
            encryption_key=key
        )

        # Create SSM parameters for the KMS key id, KMS bucket name and region
        string_parameter(self, 'sse_kms_key_id', key.key_id)
        string_parameter(self, 'bucket_with_sse_kms_enabled',
                         bucket.bucket_name)
        string_parameter(self, 'bucket_with_sse_kms_region', core.Aws.REGION)

        circleci_execution_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=["s3:*"], resources=["*"]))
