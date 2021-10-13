import { expect as expectCDK, matchTemplate, MatchStyle } from '@aws-cdk/assert';
import * as cdk from '@aws-cdk/core';
import * as TokenRotation from '../src/stacks/npm-token-rotation';
import { NPMTokenRotationConfig } from '../src/stacks/types';
test('Empty Stack', () => {
    const app = new cdk.App();
    // WHEN
    const config = {} as unknown as NPMTokenRotationConfig;
    const stack = new TokenRotation.NpmTokenRotationStack(app, 'MyTestStack', { config });
    // THEN
    expectCDK(stack).to(matchTemplate({ 
      "Resources": {}
    }, MatchStyle.EXACT))
});
