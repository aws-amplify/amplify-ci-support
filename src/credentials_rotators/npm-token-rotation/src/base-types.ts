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
