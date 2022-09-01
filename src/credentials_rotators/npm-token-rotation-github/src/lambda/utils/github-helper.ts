import { Octokit } from "@octokit/core";
import { retry } from "@octokit/plugin-retry";
import { assert } from "console";
import sodium from "tweetsodium";

export type BaseVariableType = {
  type: string;
  repository: string;
  variables: Record<string, string>;
};
export type RepositoryVariables = BaseVariableType & {
  type: "Repository";
};
export type EnvironmentVariables = BaseVariableType & {
  type: "Environment";
  environmentName: string;
};

const createOctokit = (token: string) => {
  const OctokitWithRetries = Octokit.plugin(retry);
  const octokit = new OctokitWithRetries({
    auth: token,
  });
  return octokit;
};

export const updateGitHubActionsSecrets = async (
  token: string,
  variables: RepositoryVariables | EnvironmentVariables
) => {
  console.info("start:updateGitHubActionsSecrets");
  for (const [envName, envValue] of Object.entries(variables.variables)) {
    if (variables.type === "Repository") {
      await updateGitHubRepositorySecret(
        variables.repository,
        token,
        envName,
        envValue
      );
    } else if ((variables.type = "Environment")) {
      await updateGitHubEnvironmentSecret(
        variables.repository,
        token,
        variables.environmentName,
        envName,
        envValue
      );
    } else {
      throw new Error(
        `Unknown type ${(variables as BaseVariableType).type} is not supported`
      );
    }
  }
  console.info("end:updateGitHubActionsSecrets");
};

const getRepoPublicKey = async (
  octokit: Octokit,
  owner: string,
  repo: string
) => {
  const response = await octokit.request(
    "GET /repos/{owner}/{repo}/actions/secrets/public-key",
    {
      owner: owner,
      repo: repo,
    }
  );

  const { key, key_id: keyId } = response.data;
  return { key, keyId };
};

const getRepoId = async (octokit: Octokit, owner: string, repo: string) => {
  const response = await octokit.request("GET /repos/{owner}/{repo}", {
    owner: "OWNER",
    repo: "REPO",
  });

  const { id } = response.data;
  return id;
};

const getEnvironmentPublicKey = async (
  octokit: Octokit,
  repoId: number,
  environment: string
) => {
  const response = await octokit.request(
    "GET /repositories/{repository_id}/environments/{environment_name}/secrets/public-key",
    {
      repository_id: repoId,
      environment_name: environment,
    }
  );

  const { key, key_id: keyId } = response.data;
  return { key, keyId };
};

const encryptSecret = (key: string, value: string) => {
  // Convert the message and key to Uint8Array's (Buffer implements that interface)
  const messageBytes = Buffer.from(value);
  const keyBytes = Buffer.from(key, "base64");

  // Encrypt using LibSodium.
  const encryptedBytes = sodium.seal(messageBytes, keyBytes);

  // Base64 the encrypted secret
  const encrypted = Buffer.from(encryptedBytes).toString("base64");

  return encrypted;
};

/**
 * Creates a new repository secret if missing and adds/updates the secret
 * @param repository repository to publish new secrets to
 * @param token GitHub token
 * @param secretName the name of the secret
 * @param secretValue the value of the secret
 * @returns
 */
export const updateGitHubRepositorySecret = async (
  repository: string,
  token: string,
  secretName: string,
  secretValue: string
) => {
  const [owner, repo] = repository.split("/");
  assert(
    owner && repo,
    "Could not read repository information. Format: {owner}/{repo}"
  );

  try {
    console.info("start:updateGitHubRepositorySecret");
    assert(repository, "repository is needed");
    assert(token, "token is needed");
    assert(secretName, "secretName is required");
    assert(secretValue, "secretValue is required");

    const octokit = createOctokit(token);

    const { keyId, key } = await getRepoPublicKey(octokit, repo, owner);

    const encryptedValue = encryptSecret(key, secretValue);

    const response = await octokit.request(
      "PUT /repos/{owner}/{repo}/actions/secrets/{secret_name}",
      {
        owner,
        repo,
        secret_name: secretName,
        encrypted_value: encryptedValue,
        key_id: keyId,
      }
    );

    return response.status === 201;
  } catch (e) {
    const message = (e as Error).message;
    console.error("Updating secrets to GitHub failed. Message:", message);
    throw new Error(message);
  }
};

/**
 * Creates a new repository secret if missing and adds/updates the secret
 * @param repository repository to publish new secrets to
 * @param token GitHub token
 * @param secretName the name of the secret
 * @param secretValue the value of the secret
 * @returns
 */
export const updateGitHubEnvironmentSecret = async (
  repository: string,
  token: string,
  environmentName: string,
  secretName: string,
  secretValue: string
): Promise<boolean> => {
  const [owner, repo] = repository.split("/");

  console.info("start:updateGitHubEnvironmentSecret");
  assert(repository, "repository is needed");
  assert(token, "token is needed");
  assert(environmentName, "environmentName is required");
  assert(secretName, "secretName is required");
  assert(secretValue, "secretValue is required");

  try {
    const octokit = createOctokit(token);

    const repoId = await getRepoId(octokit, owner, repo);
    console.log("Retrieved repo id", repoId);

    const { keyId, key } = await getEnvironmentPublicKey(
      octokit,
      repoId,
      owner
    );

    const encryptedValue = encryptSecret(key, secretValue);

    const response = await octokit.request(
      "PUT /repositories/{repository_id}/environments/{environment_name}/secrets/{secret_name}",
      {
        repository_id: repoId,
        environment_name: environmentName,
        secret_name: secretName,
        encrypted_value: encryptedValue,
        key_id: keyId,
      }
    );

    console.info("end:updateGitHubEnvironmentSecret");
    return response.status === 201;
  } catch (e) {
    const message = (e as Error).message;
    console.error(
      "Updating environment secrets to GitHub failed. Message:",
      message
    );
    throw new Error(message);
  }
};
