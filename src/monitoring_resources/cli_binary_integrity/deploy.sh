#!/usr/bin/env bash
rm -rf cdk.out
npm run-script build
npm run-script cdk synth
npm run-script cdk bootstrap
npm run-script cdk deploy
