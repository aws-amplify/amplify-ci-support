export type RotatableSecrets = {
  arn: string;
  secretKey: string;
};

export type SecretDetail = RotatableSecrets & {
  roleArn?: string;
};

export type TokenPublishGitHubRepoConfig = {
  type: "Repository";
  owner: string;
  repo: string;
  variableName: string;
  githubToken: SecretDetail;
};

export type TokenPublishGitHubEnvironmentConfig = {
  type: "Environment";
  owner: string;
  repo: string;
  environmentName: string;
  variableName: string;
  githubToken: SecretDetail;
};

export type TokenPublishGitHubConfig =
  | TokenPublishGitHubRepoConfig
  | TokenPublishGitHubEnvironmentConfig;

export type AccessTokenItem = SecretDetail & {
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
