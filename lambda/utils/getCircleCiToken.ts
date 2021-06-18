const AWS = require("aws-sdk");

const getCircleCiToken = async () => {
  const { SECRET_ARN, SECRET_KEY } = process.env;
  console.assert(SECRET_ARN, "SECRET_ARN environment variable must be set");
  console.assert(SECRET_KEY, "SECRET_KEY environment variable must be set");

  const secretsManager = new AWS.SecretsManager();
  const secret = await secretsManager
    .getSecretValue({
      SecretId: SECRET_ARN!.trim()
    })
    .promise();
  const secretData = JSON.parse(secret.SecretString!);
  return secretData[SECRET_KEY!];
};

export default getCircleCiToken;
