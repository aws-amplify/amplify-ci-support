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
  const promiseFns = config.circleCiConfigs.map(circleCiConfig => {
    return async () => {
      const credentials = await generateTemporaryKey(circleCiConfig.roleName);
      console.log(credentials);
      await updateCircleCiEnvironmentVariables(
        circleCiConfig as CircleCiConfig,
        credentials,
        token
      );
    };
  });

  for (let i = 0; i < promiseFns.length; i++) {
    await promiseFns[i]();
  }
};
