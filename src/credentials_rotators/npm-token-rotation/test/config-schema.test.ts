import * as Utils from "../src/lambda/utils/utils";
import path from "path";
import fs from "fs";

// assertSecretAccess will try to hit a real backend. Mock it out.
jest
  .spyOn(Utils, "assertSecretAccess")
  .mockImplementation(async () => {});

describe("Config schema", () => {
  it("accepts config.sample.json", async () => {
    const content = fs.readFileSync(
      path.resolve(__dirname, "../config.sample.json"),
      {
        encoding: "utf-8",
      }
    );
    const config = JSON.parse(content);
    const result = await Utils.validateConfiguration(config);

    expect(result).toBeTruthy();
  });
});
