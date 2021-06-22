import { CircleCiConfig } from "./updateCircleCiEnvironmentVariable";
export declare type E2eTokenRotationConfig = {
  circleCiToken: {
    arn: string;
    secretKey: string;
  };
  circleCiConfigs: CircleCiConfig[];
  alarmSubscriptions: string[];
};
export declare const loadConfiguration: (
  configFile: string
) => E2eTokenRotationConfig;
export declare const validateConfiguration: (payload: any) => boolean;
