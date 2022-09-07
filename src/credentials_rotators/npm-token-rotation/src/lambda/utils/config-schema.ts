// Schema is automatically generated using:
// % npx ts-json-schema-generator --path src/config-types.ts --type NPMTokenRotationConfig

export const schema = {
  $ref: "#/definitions/NPMTokenRotationConfig",
  $schema: "http://json-schema.org/draft-07/schema#",
  definitions: {
    AccessTokenItem: {
      additionalProperties: false,
      properties: {
        arn: {
          type: "string",
        },
        publishConfig: {
          $ref: "#/definitions/TokenPublishGitHubConfig",
        },
        roleArn: {
          type: "string",
        },
        secretKey: {
          type: "string",
        },
        slackWebHookConfig: {
          $ref: "#/definitions/SecretDetail",
        },
      },
      required: ["arn", "publishConfig", "secretKey", "slackWebHookConfig"],
      type: "object",
    },
    AccessTokenRotationConfig: {
      additionalProperties: false,
      properties: {
        alarmSubscriptions: {
          items: {
            type: "string",
          },
          type: "array",
        },
        secrets: {
          items: {
            $ref: "#/definitions/AccessTokenItem",
          },
          type: "array",
        },
      },
      required: ["secrets", "alarmSubscriptions"],
      type: "object",
    },
    NPMTokenRotationConfig: {
      additionalProperties: false,
      properties: {
        npmAccessTokenSecrets: {
          $ref: "#/definitions/AccessTokenRotationConfig",
        },
        npmLoginPasswordSecret: {
          $ref: "#/definitions/SecretDetail",
        },
        npmLoginUsernameSecret: {
          $ref: "#/definitions/SecretDetail",
        },
        npmOtpSeedSecret: {
          $ref: "#/definitions/SecretDetail",
        },
      },
      required: [
        "npmLoginUsernameSecret",
        "npmLoginPasswordSecret",
        "npmOtpSeedSecret",
        "npmAccessTokenSecrets",
      ],
      type: "object",
    },
    SecretDetail: {
      additionalProperties: false,
      properties: {
        arn: {
          type: "string",
        },
        roleArn: {
          type: "string",
        },
        secretKey: {
          type: "string",
        },
      },
      required: ["arn", "secretKey"],
      type: "object",
    },
    TokenPublishGitHubConfig: {
      anyOf: [
        {
          $ref: "#/definitions/TokenPublishGitHubRepoConfig",
        },
        {
          $ref: "#/definitions/TokenPublishGitHubEnvironmentConfig",
        },
      ],
    },
    TokenPublishGitHubEnvironmentConfig: {
      additionalProperties: false,
      properties: {
        environmentName: {
          type: "string",
        },
        githubToken: {
          $ref: "#/definitions/SecretDetail",
        },
        owner: {
          type: "string",
        },
        repo: {
          type: "string",
        },
        secretName: {
          type: "string",
        },
        type: {
          const: "Environment",
          type: "string",
        },
      },
      required: [
        "environmentName",
        "githubToken",
        "owner",
        "repo",
        "secretName",
        "type",
      ],
      type: "object",
    },
    TokenPublishGitHubRepoConfig: {
      additionalProperties: false,
      properties: {
        githubToken: {
          $ref: "#/definitions/SecretDetail",
        },
        owner: {
          type: "string",
        },
        repo: {
          type: "string",
        },
        secretName: {
          type: "string",
        },
        type: {
          const: "Repository",
          type: "string",
        },
      },
      required: ["githubToken", "owner", "repo", "secretName", "type"],
      type: "object",
    },
  },
};
