const axios = require("axios");

const updateCircleCiContext = async (
  baseUrl: string,
  contextId: string,
  token: string,
  keyName: string,
  keyValue: string
) => {
  return await axios.put(
    `${baseUrl}/context/${contextId}/environment-variable/${keyName}`,
    {
      value: keyValue
    },
    {
      headers: {
        "Circle-Token": token,
        "content-type": "application/json"
      }
    }
  );
};

export default updateCircleCiContext;
