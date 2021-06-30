import * as config from "../config.json";
import generateTemporaryKey from "./utils/generateTemporaryKey";
import getCircleCiToken from "./utils/getCircleCiToken";
import updateCircleCiEnvironmentVariables, {
  CircleCiConfig
} from "./utils/updateCircleCiEnvironmentVariable";

exports.handler = async function() {
  const token = await getCircleCiToken(
    config.circleCiToken.arn,
    config.circleCiToken.secretKey
  );
  const promises = config.circleCiConfigs.map(async circleCiConfig => {
    const credentials = await generateTemporaryKey(circleCiConfig.roleName);
    console.log(credentials);
    await updateCircleCiEnvironmentVariables(
      circleCiConfig as CircleCiConfig,
      credentials,
      token
    );
  });

  for (let i = 0; i < promises.length; i++) {
    await promises[i];
  }
};