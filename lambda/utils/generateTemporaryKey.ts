import { AccessKeyMetadata, ListAccessKeysResponse } from "aws-sdk/clients/iam";
import IAM = require("aws-sdk/clients/iam");

const AWS = require("aws-sdk");
const generateTemporaryKey = async (roleName: string) => {
  const {
    E2E_USERNAME,
    CREATE_ACCESS_KEY_TIMEOUT,
    TOKEN_TTL_HOURS,
    ROLE_PREFIX
  } = process.env;

  console.assert(E2E_USERNAME, "E2E_USERNAME environment variable must be set");
  console.assert(ROLE_PREFIX, "ROLE_PREFIX environment variable must be set");
  console.assert(
    CREATE_ACCESS_KEY_TIMEOUT,
    "CREATE_ACCESS_KEY_TIMEOUT environment variable must be set"
  );
  console.assert(
    TOKEN_TTL_HOURS,
    "TOKEN_TTL_HOURS environment variable must be set"
  );

  const iam: IAM = new AWS.IAM();
  // Remove any stale or manually generated access keys tied to the user
  const staleAccessKeys: ListAccessKeysResponse = await iam
    .listAccessKeys({
      UserName: E2E_USERNAME
    })
    .promise();

  try {
    await Promise.all(
      staleAccessKeys.AccessKeyMetadata.map(
        async (accessKey: AccessKeyMetadata) => {
          await iam
            .deleteAccessKey({
              UserName: E2E_USERNAME,
              AccessKeyId: accessKey.AccessKeyId!
            })
            .promise();
        }
      )
    );
  } catch (e) {
    // if the access key is deleted, ignore the error
    if (e.code !== "NoSuchEntity") throw e;
  }

  function sleep(ms: number) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
  await sleep(parseInt(CREATE_ACCESS_KEY_TIMEOUT!));

  const sts = new AWS.STS({});
  const date = new Date();
  const identifier = `CredentialRotationLambda-${date.getFullYear()}${date.getMonth()}${date.getDay()}${date.getHours()}${date.getMinutes()}${date.getSeconds()}`;
  const role = await iam
    .getRole({ RoleName: `${ROLE_PREFIX}${roleName}` })
    .promise();
  const creds = await sts
    .assumeRole({
      RoleArn: role.Role.Arn,
      DurationSeconds: 1 * 60 * 60,
      RoleSessionName: identifier
    })
    .promise();
  await sleep(parseInt(CREATE_ACCESS_KEY_TIMEOUT!));
  return creds.Credentials;
};

export default generateTemporaryKey;
