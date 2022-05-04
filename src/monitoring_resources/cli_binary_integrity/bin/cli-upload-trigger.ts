#!/usr/bin/env node
import 'source-map-support/register';
import { App } from 'aws-cdk-lib';

import { CliUploadTriggerStack } from '../lib/cli-upload-trigger';

const app = new App();
if (!process.env.S3_ACCOUNT_ID || !process.env.S3_ACCOUNT_REGION) {
   throw new Error('S3_ACCOUNT_ID and S3_ACCOUNT_REGION environment variables must be set.');
}
new CliUploadTriggerStack(app, 'CliUploadTriggerStack', {
   env: { account: process.env.S3_ACCOUNT_ID, region: process.env.S3_ACCOUNT_REGION },
});