export type RotatableSecrets = {
  arn: string;
  secretKey: string;
};

export type SecretDetail = RotatableSecrets & {
  roleArn?: string;
};

export type TokenPublishCircleCIContextConfig = {
  type: "Context";
  contextName: string;
  slug: string;
  variableName: string;
  circleCiToken: SecretDetail;
  githubToken: SecretDetail;
};

export type TokenPublishCircleCIEnvironmentConfig = {
  type: "Environment";
  slug: string;
  projectName: string;
  variableName: string;
  circleCiToken: SecretDetail;
  githubToken: SecretDetail;
};

export type AccessTokenItem = RotatableSecrets & {
  publishConfig:
    | TokenPublishCircleCIContextConfig
    | TokenPublishCircleCIEnvironmentConfig;
  slackWebHookConfig: SecretDetail;
  roleArn?: string;
};

export type AccessTokenRotationConfig = {
  secrets: AccessTokenItem[];
  alarmSubscriptions: string[];
};

export type NPMTokenRotationConfig = {
  npmLoginUsernameSecret: SecretDetail;
  npmLoginPasswordSecret: SecretDetail;
  npmOtpSeedSecret: SecretDetail;
  npmAccessTokenSecrets: AccessTokenRotationConfig;
};

export type TokenRotationStepFnEvent = {
  tokenEvent: string;
  secretArn: string;
};
