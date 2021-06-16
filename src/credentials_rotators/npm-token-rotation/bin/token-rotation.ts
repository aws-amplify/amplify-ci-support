#!/usr/bin/env node
import "source-map-support/register";
import * as cdk from "@aws-cdk/core";
import * as path from "path";
import * as util from "../src/lambda/utils/utils";
import { NpmTokenRotationStack } from "../src/stacks/npm-token-rotation";

const app = new cdk.App();
const config = util.loadConfiguration(
  path.join(__dirname, "..", "secret_config.json")
);
new NpmTokenRotationStack(app, "npm-token-rotation", {
  config,
});
