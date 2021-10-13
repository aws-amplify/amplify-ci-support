import * as sodium from 'tweetsodium';
import { Octokit } from '@octokit/rest';
import { GithubTokenConfig } from '../npm-token-rotation/src/stacks/types';

//https://docs.github.com/en/rest/reference/actions#create-or-update-a-repository-secret

export const updateGithubEnvironmentSecret = async (gitubConfig: GithubTokenConfig , secret: string, secretKey: string) =>  {
    const octokit = new Octokit({
        auth: gitubConfig.token,
    });

    const publicKey = await octokit.actions.getRepoPublicKey({
        owner: gitubConfig.owner,
        repo: gitubConfig.repo,
    });
    
    const messageBytes = Buffer.from(secret);
    const keyBytes = Buffer.from(publicKey.data.key, 'base64');


    const encryptedBytes = sodium.seal(messageBytes, keyBytes);


    const encrypted = Buffer.from(encryptedBytes).toString('base64');

    
    await octokit.actions.createOrUpdateRepoSecret({
        owner: gitubConfig.owner,
        repo: gitubConfig.repo,
        secret_name: secretKey,
        encrypted_value: encrypted,
        key_id: publicKey.data.key_id,
    });
};
