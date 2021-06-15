#!/usr/bin/env bash
npm run-script build
npx cdk synth
npx cdk bootstrap
npx cdk deploy
