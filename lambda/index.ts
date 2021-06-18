import generateTemporaryKey from "./utils/generateTemporaryKey";
import getCircleCiContextId from "./utils/getCircleCiContextId";
import getCircleCiToken from "./utils/getCircleCiToken";
import updateCircleCiContext from "./utils/updateCircleCiContext";

exports.handler = async function() {
  const CIRCLE_CI_BASE_URL = "https://circleci.com/api/v2";
  const {
    CIRCLECI_SECRET_KEY_ID_VARIABLE,
    CIRCLECI_SECRET_KEY_VARIABLE
  } = process.env;
  console.assert(
    CIRCLECI_SECRET_KEY_ID_VARIABLE,
    "CIRCLECI_SECRET_KEY_ID_VARIABLE environment variable must be set"
  );
  console.assert(
    CIRCLECI_SECRET_KEY_VARIABLE,
    "CIRCLECI_SECRET_KEY_VARIABLE environment variable must be set"
  );

  const credentials = await generateTemporaryKey();

  const mappings = {
    [CIRCLECI_SECRET_KEY_ID_VARIABLE!]: credentials.AccessKeyId,
    [CIRCLECI_SECRET_KEY_VARIABLE!]: credentials.SecretAccessKey
  };

  const token = await getCircleCiToken();
  const contextId = await getCircleCiContextId(CIRCLE_CI_BASE_URL, token);
  const promises = Object.keys(mappings).map(async key => {
    return await updateCircleCiContext(
      CIRCLE_CI_BASE_URL,
      contextId,
      token,
      key,
      mappings[key]
    );
  });
  await Promise.all(promises);
};
