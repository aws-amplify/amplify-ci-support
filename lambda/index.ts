exports.handler = async function() {
  const AWS = require("aws-sdk");
  const https = require("https");

  const {
    CIRCLECI_KEY,
    CIRCLE_PROJECT_USERNAME,
    CIRCLE_PROJECT_REPONAME,
    E2E_ROLE_ARN,
    E2E_USERNAME,
    TOKEN_TTL_HOURS,
  } = process.env;

  const iam = new AWS.IAM();
  const userCredentials = (await iam
    .createAccessKey({
      UserName: E2E_USERNAME,
    })
    .promise()).AccessKey;

  function sleep(ms: number) {
    // Although the key creation via IAM immediately returns credentials, it takes a little time
    // (on the order of ~10s) before the key is propagated widely enough to allow it to be used in an
    // sts:AssumeRole call. Unfortunately, there isn't a good way to test for the propagation other
    // than simply trying to use them, but in practice we haven't seen these become available any
    // sooner than ~8s after creation.
    // The get_session_credentials call is wrapped in a @retry, so even if this hardcoded timeout isn't
    // quite long enough, the subsequent downstream calls will still gracefully handle propagation
    // delay.
    return new Promise((resolve) => setTimeout(resolve, ms));
  }
  await sleep(10000);

  const sts = new AWS.STS({
    accessKeyId: userCredentials.AccessKeyId,
    secretAccessKey: userCredentials.SecretAccessKey,
  });
  const date = new Date();
  const identifier = `CredentialRotationLambda-${date.getFullYear()}${date.getMonth()}${date.getDay()}${date.getHours()}${date.getMinutes()}${date.getSeconds()}`;
  const creds = await sts
    .assumeRole({
      RoleArn: E2E_ROLE_ARN,
      DurationSeconds: +TOKEN_TTL_HOURS! * 60 * 60,
      RoleSessionName: identifier,
    })
    .promise();

  await iam
    .deleteAccessKey({
      UserName: E2E_USERNAME,
      AccessKeyId: userCredentials.AccessKeyId,
    })
    .promise();

  const accessKeyIdData = JSON.stringify({
    name: "AWS_ACCESS_KEY_ID",
    value: creds.Credentials.AccessKeyId,
  });

  const accessKeySecretData = JSON.stringify({
    name: "AWS_SECRET_ACCESS_KEY",
    value: creds.Credentials.SecretAccessKey,
  });

  const promises = [accessKeyIdData, accessKeySecretData].map(async (data) => {
    const options = {
      hostname: "circleci.com",
      port: 443,
      path: `/api/v1.1/project/github/${CIRCLE_PROJECT_USERNAME}/${CIRCLE_PROJECT_REPONAME}/envvar?circle-token=${CIRCLECI_KEY}`,
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Content-Length": data.length,
      },
    };

    function doRequest(options: any, data: any) {
      return new Promise((resolve, reject) => {
        const req = https.request(options, (res: any) => {
          res.setEncoding("utf8");
          let responseBody = "";

          res.on("data", (chunk: string) => {
            responseBody += chunk;
          });

          res.on("end", () => {
            resolve(responseBody);
          });
        });

        req.on("error", (err: Error) => {
          reject(err);
        });

        req.write(data);
        req.end();
      });
    }
    return await doRequest(options, data);
  });
  await Promise.all(promises);
};
