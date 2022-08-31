import { expect as expectCDK, matchTemplate, MatchStyle } from '@aws-cdk/assert';
import * as cdk from '@aws-cdk/core';
import * as TokenRotation from '../src/token-rotation-stack';

test('Empty Stack', () => {
    const app = new cdk.App();
    // WHEN
    const stack = new TokenRotation.TokenRotationStack(app, 'MyTestStack');
    // THEN
    expectCDK(stack).to(matchTemplate({
      "Resources": {}
    }, MatchStyle.EXACT))
});
