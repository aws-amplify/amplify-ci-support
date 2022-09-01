import { Octokit } from "@octokit/core";
import { retry } from "@octokit/plugin-retry";
import { assert } from "console";
import sodium from "libsodium-wrappers";
import {
  BaseUpdateGitHubSecretsParam,
  UpdateGitHubSecretsParam,
} from "../../stacks/types";

const createOctokit = (githubToken: string) => {
  const OctokitWithRetries = Octokit.plugin(retry);
  const octokit = new OctokitWithRetries({
    auth: githubToken,
  });
  return octokit;
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
    owner,
    repo,
  });

  const { id } = response.data;
  return id;
};

const getEnvironmentPublicKey = async (
  octokit: Octokit,
  repoId: number,
  environment: string
) => {
  console.log(environment);
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

const encryptSecret = async (key: string, value: string) => {
  // prepare libsodium
  await sodium.ready;

  // Convert Secret & Base64 key to Uint8Array
  const keyBytes = sodium.from_base64(key, sodium.base64_variants.ORIGINAL);
  const secretBytes = sodium.from_string(value);

  // Encrypt using LibSodium.
  const encryptedBytes = sodium.crypto_box_seal(secretBytes, keyBytes);

  // Convert encrypted Uint8Array to Base64
  const encrypted = sodium.to_base64(
    encryptedBytes,
    sodium.base64_variants.ORIGINAL
  );

  return encrypted;
};

/**
 * Creates a new repository secret if missing and adds/updates the secret
 * @param repository repository to publish new secrets to
 * @param githubToken GitHub token
 * @param secretName the name of the secret
 * @param secretValue the value of the secret
 * @returns
 */
const updateGitHubRepositorySecret = async (
  owner: string,
  repo: string,
  githubToken: string,
  secretName: string,
  secretValue: string
) => {
  try {
    console.info("start:updateGitHubRepositorySecret");
    assert(owner, "owner is needed");
    assert(repo, "repo is needed");
    assert(githubToken, "token is needed");
    assert(secretName, "secretName is required");
    assert(secretValue, "secretValue is required");

    const octokit = createOctokit(githubToken);

    const { keyId, key } = await getRepoPublicKey(octokit, owner, repo);

    const encryptedValue = await encryptSecret(key, secretValue);

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
    console.error(e);
    // console.error("Updating secrets to GitHub failed. Message:", message);
    throw new Error(message);
  }
};

/**
 * Creates a new environment secret if missing and adds/updates the secret
 * @param repository repository to publish new secrets to
 * @param githubToken GitHub token
 * @param secretName the name of the secret
 * @param secretValue the value of the secret
 * @returns
 */
const updateGitHubEnvironmentSecret = async (
  owner: string,
  repo: string,
  githubToken: string,
  environmentName: string,
  secretName: string,
  secretValue: string
): Promise<boolean> => {
  console.info("start:updateGitHubEnvironmentSecret");
  assert(owner, "owner is needed");
  assert(repo, "repo is needed");
  assert(githubToken, "token is needed");
  assert(environmentName, "environmentName is required");
  assert(secretName, "secretName is required");
  assert(secretValue, "secretValue is required");

  try {
    const octokit = createOctokit(githubToken);

    const repoId = await getRepoId(octokit, owner, repo);

    const { keyId, key } = await getEnvironmentPublicKey(
      octokit,
      repoId,
      environmentName
    );

    const encryptedValue = await encryptSecret(key, secretValue);

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
    console.error("Updating environment secrets to GitHub failed. Error:", e);
    throw new Error(message);
  }
};

export const updateGitHubActionsSecrets = async (
  config: UpdateGitHubSecretsParam
) => {
  console.info("start:updateGitHubActionsSecrets");

  const { githubToken, owner, repo, type } = config;

  for (const [secretName, secretValue] of Object.entries(config.secrets)) {
    if (type === "Repository") {
      await updateGitHubRepositorySecret(
        owner,
        repo,
        githubToken,
        secretName,
        secretValue
      );
    } else if (type === "Environment") {
      const { environmentName } = config;

      await updateGitHubEnvironmentSecret(
        owner,
        repo,
        githubToken,
        environmentName,
        secretName,
        secretValue
      );
    } else {
      throw new Error(
        `Unknown type ${
          config as BaseUpdateGitHubSecretsParam
        } is not supported`
      );
    }
  }
  console.info("end:updateGitHubActionsSecrets");
};
