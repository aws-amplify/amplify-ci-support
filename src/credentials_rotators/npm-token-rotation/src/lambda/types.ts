import { GitHubRepoInfo, SecretDetail } from '../base-types';
import { AccessTokenRotationConfig } from '../config-types';

/**
 * Parameters to updateGitHubSecrets call. These are used after `githubToken`
 * has been fetched.
 */
export type SecretValuesMap = Record<string, string>; //maps secret name to secret value

export type BaseUpdateGitHubSecretsParam = GitHubRepoInfo & {
  type: string;
  secrets: SecretValuesMap;
  githubToken: string;
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

export type TokenRotationStepFnEvent = {
  tokenEvent: string;
  secretArn: string;
};

export type NPMTokenRotationConfig = {
  npmLoginUsernameSecret: SecretDetail;
  npmLoginPasswordSecret: SecretDetail;
  npmOtpSeedSecret: SecretDetail;
  npmAccessTokenSecrets: AccessTokenRotationConfig;
};
