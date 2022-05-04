const crypto = require('crypto');
const fs = require('fs');
const stream = require('stream');
const util = require('util');
const { createGunzip } = require('zlib');
const tar = require('tar-stream');
const { KMSClient, MessageType, SigningAlgorithmSpec, VerifyCommand } = require("@aws-sdk/client-kms");
const AWS = require('aws-sdk');
const { Readable } = require('stream');

const s3 = new AWS.S3();
const kms = new KMSClient({ region: "us-east-1" });
const pipeline = util.promisify(stream.pipeline);

exports.handler = async function (event: any) {
  const verifyBinary = async (binaryBuffer: Buffer, signatureDigestBuffer: Buffer): Promise<void> => {
    const hashSum = crypto.createHash('sha512');
    hashSum.update(binaryBuffer);
    const message = hashSum.digest();

    const command = new VerifyCommand({
      KeyId: 'alias/s3-sign-verify',
      Message: new Uint8Array(message),
      MessageType: MessageType.DIGEST,
      Signature: new Uint8Array(signatureDigestBuffer),
      SigningAlgorithm: SigningAlgorithmSpec.RSASSA_PSS_SHA_512,
    });
    const data = await kms.send(command);
    if (!data?.SignatureValid) {
      throw new Error(`Unable to verify integrity of ${this.binaryPath}`);
    }
  }
  const extract = () => {
    const extract = tar.extract();
    const chunks: Uint8Array[] = [];
    const signatureChunks: Uint8Array[] = [];
    extract.on('entry', (header: any, extractStream: any, next: any) => {
      if (header.type === 'file') {
        extractStream.on('data', (chunk: any) => {
          if (header.name === this.signatureDigestFilename) {
            signatureChunks.push(chunk);
          } else {
            chunks.push(chunk);
          }
        });
      }
      extractStream.on('end', () => {
        next();
      });

      extractStream.resume();
    });
    extract.on('finish', async () => {
      await verifyBinary(Buffer.concat(chunks), Buffer.concat(signatureChunks));
    });
    return extract;
  }
  const promises = event.Records.map(async (record: any) => {
      const object = await s3.getObject({
          Bucket: record.s3.bucket.name,
          Key: record.s3.object.key,
      }).createReadStream();
      await pipeline(
        object,
        createGunzip(),
        extract(),
      );
  });
  await Promise.all(promises);
};