import { CircleCiConfig } from "./updateCircleCiEnvironmentVariable";
import axios from "axios";

const getCircleCiContextId = async (
  config: CircleCiConfig,
  baseUrl: string,
  token: string
) => {
  const url = `${baseUrl}/context`;
  const response = await axios.get(url, {
    headers: {
      "Circle-Token": token,
      "content-type": "application/json"
    },
    params: {
      "owner-slug": config.slug,
      "owner-type": "organization"
    }
  });
  const idMap: { [key: string]: string } = (response.data.items as {
    id: string;
    name: string;
  }[]).reduce((acc, context) => ({ ...acc, [context.name]: context.id }), {});
  const contextId = idMap[config.name!];
  if (!contextId) {
    throw new Error(`Context with name '${config.name}' does not exist`);
  }
  return contextId;
};

export default getCircleCiContextId;
