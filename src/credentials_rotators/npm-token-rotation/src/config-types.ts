import { GitHubRepoInfo, SecretDetail } from "./base-types";

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

export type AccessTokenItem = SecretDetail & {
  publishConfig: TokenPublishGitHubConfig;
  slackWebHookConfig?: SecretDetail;
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
