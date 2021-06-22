import { CircleCiConfig } from "./updateCircleCiEnvironmentVariable";
declare const getCircleCiContextId: (
  config: CircleCiConfig,
  baseUrl: string,
  token: string
) => Promise<string>;
export default getCircleCiContextId;
