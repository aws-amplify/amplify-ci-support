import { expect as expectCDK, matchTemplate, MatchStyle } from '@aws-cdk/assert';
import * as cdk from '@aws-cdk/core';
import * as TokenRotation from '../src/stacks/npm-token-rotation';

test('Empty Stack', () => {
    const app = new cdk.App();
    // WHEN
    const stack = new TokenRotation.NpmTokenRotationStack(app, 'MyTestStack', {config: {} as any});
    // THEN
    expectCDK(stack).to(matchTemplate({
      "Resources": {}
    }, MatchStyle.EXACT))
});
