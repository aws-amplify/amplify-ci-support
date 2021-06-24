import { AwsCredentials } from "aws-sdk/clients/gamelift";
import getCircleCiContextId from "./getCircleCiContextId";
import axios from "axios";

export type CircleCiConfig = {
  type: "Context" | "Environment";
  name: string;
  slug: string;
  secretKeyIdVariableName: string;
  secretKeyVariableName: string;
  sessionTokenVariableName: string;
  roleName: string;
  permissions: {
    resources: string[];
    actions: string[];
    effect: string;
  }[];
};

const CIRCLE_CI_BASE_URL = "https://circleci.com/api/v2";

const updateCircleCiEnvironmentVariable = async (
  config: CircleCiConfig,
  credentials: AwsCredentials,
  token: string
) => {
  const headers = {
    headers: {
      "Circle-Token": token,
      "content-type": "application/json"
    }
  };
  const mappings = {
    [config.secretKeyIdVariableName!]: credentials.AccessKeyId,
    [config.secretKeyVariableName!]: credentials.SecretAccessKey,
    [config.sessionTokenVariableName!]: credentials.SessionToken
  };

  let promises: Promise<any>[] = [];
  if (config.type === "Context") {
    const contextId = await getCircleCiContextId(
      config,
      CIRCLE_CI_BASE_URL,
      token
    );
    promises = Object.keys(mappings).map(async key => {
      return await axios.put(
        `${CIRCLE_CI_BASE_URL}/context/${contextId}/environment-variable/${key}`,
        {
          value: mappings[key]
        },
        headers
      );
    });
  } else {
    promises = Object.keys(mappings).map(async key => {
      return await axios.put(
        `${CIRCLE_CI_BASE_URL}/project/${config.slug}/${config.name}/envvar`,
        {
          name: key,
          value: mappings[key]
        },
        headers
      );
    });
  }
  await Promise.all(promises);
};

export default updateCircleCiEnvironmentVariable;
