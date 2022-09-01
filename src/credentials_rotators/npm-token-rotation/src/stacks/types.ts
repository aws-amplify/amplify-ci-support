export type RotatableSecrets = {
  arn: string;
  secretKey: string;
};

export type SecretDetail = RotatableSecrets & {
  roleArn?: string;
};

export type GitHubTokenSecretDetail = {
  githubToken: SecretDetail;
};

export type GitHubRepoInfo = {
  owner: string;
  repo: string;
};
/** Publish configs */
export type TokenPublishGitHubRepoConfig = GitHubRepoInfo & {
  type: "Repository";
  variableName: string;
  githubToken: SecretDetail;
};

export type TokenPublishGitHubEnvironmentConfig = GitHubRepoInfo & {
  type: "Environment";
  environmentName: string;
  variableName: string;
  githubToken: SecretDetail;
};

export type TokenPublishGitHubConfig =
  | TokenPublishGitHubRepoConfig
  | TokenPublishGitHubEnvironmentConfig;

/**
 * Parameters to updateGitHubSecrets call. These are used after `githubToken`
 * has been fetched.
 */
export type SecretValuesMap = Record<string, string>; //maps secret name to secret value

export type BaseUpdateGitHubSecretsParam = GitHubRepoInfo & {
  type: string;
  variables: SecretValuesMap;
  token: string;
};

export type UpdateGitHubRepoSecretsParam = BaseUpdateGitHubSecretsParam & {
  type: "Repository";
};

export type UpdateGitHubEnvSecretsParam = BaseUpdateGitHubSecretsParam & {
  type: "Environment";
  environmentName: string;
};

export type UpdateGitHubSecretsParam =
  | UpdateGitHubRepoSecretsParam
  | UpdateGitHubEnvSecretsParam;

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
