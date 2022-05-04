import { App, Stack, StackProps } from 'aws-cdk-lib';
import { Bucket, EventType } from 'aws-cdk-lib/aws-s3';
import { Function, Code, Runtime } from 'aws-cdk-lib/aws-lambda';
import { S3EventSource } from 'aws-cdk-lib/aws-lambda-event-sources';
import { PolicyStatement, Policy } from 'aws-cdk-lib/aws-iam';

export class CliUploadTriggerStack extends Stack {
  constructor(app: App, id: string, props?: StackProps) {
    super(app, id, props);
    const bucket = Bucket.fromBucketName(
      this,
      'aws-amplify-cli-do-not-delete',
      'aws-amplify-cli-do-not-delete',
    );

    const lambdaFunction = new Function(this, 'Function', {
      code: Code.fromAsset('src'),
      handler: 'index.handler',
      functionName: 'BucketPutHandler',
      runtime: Runtime.NODEJS_14_X,
    });

    const s3GetObjectPolicy = new PolicyStatement({
      actions: ['s3:getObject'],
      resources: [`${bucket.bucketArn}/*`],
    });

    lambdaFunction.role?.attachInlinePolicy(
      new Policy(this, 'get-object-policy', {
        statements: [s3GetObjectPolicy],
      }),
    );

    const s3PutEventSource = new S3EventSource(bucket as Bucket, {
      events: [
        EventType.OBJECT_CREATED_PUT
      ]
    });

    lambdaFunction.addEventSource(s3PutEventSource);
  }
}