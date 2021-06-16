import axios from "axios";
import { assert } from "console";

export type BaseVariableType = {
  type: string;
  slug: string;
  variables: Record<string, string>;
};
export type ContextVariables = BaseVariableType & {
  type: "Context";
  context: string;
};
export type EnvironmentVariables = BaseVariableType & {
  type: "Environment";
  projectName: string;
};

const CIRCLE_CI_BASE_URL = "https://circleci.com/api/v2";

const generateCircleCIHeaders = (token: string): Record<string, string> => {
  return {
    "Circle-Token": token,
    "content-type": "application/json",
  };
};

export const updateCircleCIEnvironmentVariables = async (
  token: string,
  variables: ContextVariables | EnvironmentVariables
) => {
  console.info("start:updateCircleCIEnvironmentVariables");
  for (const [envName, envValue] of Object.entries(variables.variables)) {
    if (variables.type === "Context") {
      await updateCircleCIContextEnvironmentVariable(
        variables.slug,
        token,
        variables.context,
        envName,
        envValue
      );
    } else if ((variables.type = "Environment")) {
      await updateCircleCIEnvironmentVariable(
        variables.slug,
        variables.projectName,
        token,
        envName,
        envValue
      );
    } else {
      throw new Error(
        `Unknown type ${(variables as BaseVariableType).type} is not supported`
      );
    }
  }
  console.info("end:updateCircleCIEnvironmentVariables");
};

/**
 * Creates a new context if missing and adds/updates the environment variable
 * @param slug slug of the project with gh/{username}/
 * @param token CircleCI token
 * @param contextName name of the context
 * @param environmentVariableName variable name
 * @param environmentVariableValue variable value
 * @returns
 */
export const updateCircleCIContextEnvironmentVariable = async (
  slug: string,
  token: string,
  contextName: string,
  environmentVariableName: string,
  environmentVariableValue: string
) => {
  try {
    console.info("start:updateCircleCIContextEnvironmentVariable");
    assert(slug, "slug is needed");
    assert(token, "token is needed");
    assert(contextName, "contextName is required");
    assert(environmentVariableName, "environmentVariableName is required");
    assert(environmentVariableValue, "environmentVariableValue is required");

    const contexts = await listContexts(slug, token);
    let contextId;
    if (Object.keys(contexts).includes(contextName)) {
      contextId = contexts[contextName];
    } else {
      contextId = await addContext(slug, token, contextName);
    }

    const response = await axios.put(
      `${CIRCLE_CI_BASE_URL}/context/${contextId}/environment-variable/${environmentVariableName}`,
      {
        value: environmentVariableValue,
      },
      {
        headers: generateCircleCIHeaders(token),
      }
    );
    console.info("start:updateCircleCIContextEnvironmentVariable");
    return response.status === 200;
  } catch (e) {
    // Todo: remove this debug statement
    console.log("value", environmentVariableValue);
    const message = `Failed to create context environment variable with error code ${e.response.status} \nmessage: ${e.response.statusText}`;
    console.error(message);
    throw new Error(message);
  }
};

/**
 *
 * @param slug slug of the project with gh/{username}/
 * @param project Project Name
 * @param token CircleCI Token
 * @param variableName Environment variable name
 * @param variableValue Environment variable value
 * @returns true if env var was created
 */
export const updateCircleCIEnvironmentVariable = async (
  slug: string,
  project: string,
  token: string,
  variableName: string,
  variableValue: string
): Promise<boolean> => {
  console.info("start:updateCircleCIEnvironmentVariable");
  const response = await axios.post(
    `${CIRCLE_CI_BASE_URL}/project/${slug}/${project}/envvar`,
    {
      name: variableName,
      value: variableValue,
    },
    {
      headers: generateCircleCIHeaders(token),
    }
  );
  console.info("end:updateCircleCIEnvironmentVariable");
  return response.status === 201;
};

export const listContexts = async (
  slug: string,
  token: string
): Promise<Record<string, string>> => {
  console.info("start:listContext");
  const url = `${CIRCLE_CI_BASE_URL}/context`;

  const response = await axios.get(url, {
    headers: generateCircleCIHeaders(token),
    params: {
      "owner-slug": slug,
      "owner-type": "organization",
    },
  });
  console.info("end:listContext");
  return (response.data.items as { id: string; name: string }[]).reduce(
    (acc, context) => ({ ...acc, [context.name]: context.id }),
    {}
  );
};

export const addContext = async (
  slug: string,
  token: string,
  contextName: string
): Promise<string> => {
  console.info("start:addContext");
  const url = `${CIRCLE_CI_BASE_URL}/context`;
  const response = await axios.post(
    url,
    {
      owner: {
        slug: slug,
        type: "organization",
      },
      name: contextName,
    },
    {
      headers: generateCircleCIHeaders(token),
    }
  );
  console.info("end:addContext");
  return response.data.id;
};
