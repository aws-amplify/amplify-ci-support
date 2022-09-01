/** Secrets Manager Types */
export type RotatableSecrets = {
  arn: string;
  secretKey: string;
};

export type SecretDetail = RotatableSecrets & {
  roleArn?: string;
};

/** GitHub specific utility types */
export type GitHubTokenSecretDetail = {
  githubToken: SecretDetail;
};

export type GitHubRepoInfo = {
  owner: string;
  repo: string;
};

/** Publish configs */
export type BaseTokenPublishGitHubConfig = GitHubRepoInfo & {
  type: string;
  secretName: string;
  githubToken: SecretDetail;
};

export type TokenPublishGitHubRepoConfig = BaseTokenPublishGitHubConfig & {
  type: "Repository";
};

export type TokenPublishGitHubEnvironmentConfig =
  BaseTokenPublishGitHubConfig & {
    type: "Environment";
    environmentName: string;
  };

export type TokenPublishGitHubConfig =
  | TokenPublishGitHubRepoConfig
  | TokenPublishGitHubEnvironmentConfig;

/** High level config objects */
export type AccessTokenItem = SecretDetail & {
  publishConfig: TokenPublishGitHubConfig;
  slackWebHookConfig: SecretDetail;
};

export type AccessTokenRotationConfig = {
  secrets: AccessTokenItem[];
  alarmSubscriptions: string[];
};
