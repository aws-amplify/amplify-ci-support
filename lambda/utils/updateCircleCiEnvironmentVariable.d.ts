import { AwsCredentials } from "aws-sdk/clients/gamelift";
export declare type CircleCiConfig = {
  type: "Context" | "Environment";
  name: string;
  slug: string;
  secretKeyIdVariableName: string;
  secretKeyVariableName: string;
  roleName: string;
  permissions: {
    resources: string[];
    actions: string[];
    effect: string;
  }[];
};
declare const updateCircleCiEnvironmentVariable: (
  config: CircleCiConfig,
  credentials: AwsCredentials,
  token: string
) => Promise<void>;
export default updateCircleCiEnvironmentVariable;
