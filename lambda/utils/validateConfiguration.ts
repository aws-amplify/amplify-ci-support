import * as fs from "fs";
import { schema } from "./config-schema";
import { CircleCiConfig } from "./updateCircleCiEnvironmentVariable";
const Ajv = require("ajv");
export type E2eTokenRotationConfig = {
  circleCiToken: {
    arn: string;
    secretKey: string;
  };
  circleCiConfigs: CircleCiConfig[];
  alarmSubscriptions: string[];
};

export const loadConfiguration = (
  configFile: string
): E2eTokenRotationConfig => {
  const content = fs.readFileSync(configFile, { encoding: "utf-8" });
  const config = JSON.parse(content);
  validateConfiguration(config);
  return config as E2eTokenRotationConfig;
};

export const validateConfiguration = (payload: any) => {
  const a = new Ajv();
  const valid = a.validate(schema, payload);
  if (!valid) {
    console.log("Configuration validation failed", a.errors);
    throw new Error("Configuration validation failed");
  }

  const validator = a.compile(schema);
  return validator(payload);
};
