import { updateGithubEnvironmentSecret } from '../../../../common-utils/github-helper';
import { NPMTokenRotationConfig, TokenRotationStepFnEvent } from '../../stacks/types';
import * as utils from '../utils/utils';
import config from '../../../config.json';

export const handler = async (event: TokenRotationStepFnEvent) => {
    try {
    const npmConfig = config as NPMTokenRotationConfig;
    const tokenDetails = utils.getTokenConfigForArn(npmConfig,  event.secretArn);
    const npmToken = await utils.getSecret(event.secretArn, tokenDetails.secretKey);
    const githubTokenSecret = tokenDetails.publishConfig.githubToken;
    const githubToken = await utils.getSecret(githubTokenSecret.arn, githubTokenSecret.secretKey, undefined, { isPlainTextValue: true });
    await updateGithubEnvironmentSecret({
        repo: 'amplify-cli-export-construct',
        owner: 'aws-amplify',
        token: githubToken,
    }, npmToken, "NPM_TOKEN");
    }catch(ex) {
        console.log(ex);
        // don't do anything if it
    }
    return event;
}