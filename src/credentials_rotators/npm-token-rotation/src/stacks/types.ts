export type RotatableSecrets = {
  arn: string;
  secretKey: string;
};

export type SecretDetail = RotatableSecrets & {
  roleArn?: string;
};

export type TokenPublishGitHubRepoConfig = {
  type: "Repository";
  repository: string;
  slug: string;
  variableName: string;
  githubToken: SecretDetail;
};

export type TokenPublishGitHubEnvironmentConfig = {
  type: "Environment";
  repository: string;
  environmentName: string;
  variableName: string;
  githubToken: SecretDetail;
};

export type AccessTokenItem = RotatableSecrets & {
  publishConfig:
    | TokenPublishGitHubRepoConfig
    | TokenPublishGitHubEnvironmentConfig;
  slackWebHookConfig: SecretDetail;
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
