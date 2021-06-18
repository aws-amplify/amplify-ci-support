const AWS = require("aws-sdk");
const axios = require("../lambda/node_modules/axios");
jest.mock("../lambda/node_modules/axios");

const createAccessKeyMock = jest.fn(() => ({
  promise: () => {
    return {
      AccessKey: "abc123"
    };
  }
}));
const deleteAccessKeyMock = jest.fn(() => {
  return { promise: () => true };
});

AWS.IAM = jest.fn(() => ({
  createAccessKey: createAccessKeyMock,
  deleteAccessKey: deleteAccessKeyMock
}));
AWS.STS = jest.fn(() => ({
  assumeRole: () => {
    return {
      promise: () => ({
        Credentials: {
          AccessKeyId: "ABC",
          SecretAccessKey: "123"
        }
      })
    };
  }
}));
const secretsManagerMock = jest.fn(() => {
  return {
    promise: () => ({
      SecretString: '{"test": "abc123"}'
    })
  };
});
AWS.SecretsManager = jest.fn(() => ({
  getSecretValue: secretsManagerMock
}));
const { handler } = require("../lambda/index");
const data = {
  data: {
    items: [
      {
        id: 123,
        name: "test"
      }
    ]
  }
};

axios.get.mockImplementation(() => Promise.resolve(data));
axios.put.mockImplementation(() => Promise.resolve(data));
describe("Lambda", () => {
  beforeAll(async () => {
    process.env.CREATE_ACCESS_KEY_TIMEOUT = "500";
    process.env.TOKEN_TTL_HOURS = "5";
    process.env.E2E_ROLE_ARN = "E2E_ROLE_ARN";
    process.env.E2E_USERNAME = "E2E_USERNAME";
    process.env.CIRCLECI_SLUG = "CIRCLECI_SLUG";
    process.env.CIRCLECI_CONTEXT_NAME = "test";
    process.env.CIRCLECI_SECRET_KEY_ID_VARIABLE =
      "CIRCLECI_SECRET_KEY_ID_VARIABLE";
    process.env.CIRCLECI_SECRET_KEY_VARIABLE = "CIRCLECI_SECRET_KEY_VARIABLE";
    process.env.SECRET_ARN = "SECRET_ARN";
    process.env.SECRET_KEY = "SECRET_KEY";
    await handler();
  });

  it("creates a new access key", async () => {
    expect(createAccessKeyMock).toBeCalledTimes(1);
  });

  it("deletes the new access key", async () => {
    expect(deleteAccessKeyMock).toBeCalledTimes(1);
  });

  it("fetches circleci api key from secretsmanager", async () => {
    expect(deleteAccessKeyMock).toBeCalledTimes(1);
  });

  it("calls in to update circle ci environment", async () => {
    expect(axios.get).toBeCalledTimes(1);
    expect(axios.put).toBeCalledTimes(2);
  });
});
