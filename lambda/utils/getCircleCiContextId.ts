const axios = require("axios");

const getCircleCiContextId = async (baseUrl: string, token: string) => {
  const { CIRCLECI_CONTEXT_NAME, CIRCLECI_SLUG } = process.env;
  console.assert(
    CIRCLECI_CONTEXT_NAME,
    "CIRCLECI_CONTEXT_NAME environment variable must be set"
  );
  console.assert(
    CIRCLECI_SLUG,
    "CIRCLECI_SLUG environment variable must be set"
  );

  const url = `${baseUrl}/context`;
  const response = await axios.get(url, {
    headers: {
      "Circle-Token": token,
      "content-type": "application/json"
    },
    params: {
      "owner-slug": CIRCLECI_SLUG,
      "owner-type": "organization"
    }
  });
  const idMap: { [key: string]: string } = (response.data.items as {
    id: string;
    name: string;
  }[]).reduce((acc, context) => ({ ...acc, [context.name]: context.id }), {});
  const contextId = idMap[CIRCLECI_CONTEXT_NAME!];
  if (!contextId) {
    throw new Error(
      `Context with name '${CIRCLECI_CONTEXT_NAME}' does not exist`
    );
  }
  return contextId;
};

export default getCircleCiContextId;
