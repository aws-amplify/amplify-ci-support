const AWS = require("aws-sdk");

const getCircleCiToken = async (arn: string, secretKey: string) => {
  const secretsManager = new AWS.SecretsManager();
  const secret = await secretsManager
    .getSecretValue({
      SecretId: arn.trim()
    })
    .promise();
  const secretData = JSON.parse(secret.SecretString!);
  return secretData[secretKey];
};

export default getCircleCiToken;
