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
const getRoleMock = jest.fn(() => {
  return {
    promise: () => ({
      Arn: "arn::role"
    })
  };
});

AWS.IAM = jest.fn(() => ({
  createAccessKey: createAccessKeyMock,
  deleteAccessKey: deleteAccessKeyMock,
  getRole: getRoleMock
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
        name: "some-context"
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
    process.env.ROLE_PREFIX = "test-";
    process.env.E2E_USERNAME = "E2E_USERNAME";
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
