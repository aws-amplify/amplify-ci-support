// Schema is automatically generated using Name: Typescript JSON schema generator using
// https://marketplace.visualstudio.com/items?itemName=marcoq.vscode-typescript-to-json-schema
// the input type for the schema is in ../../src/stacks/types.ts

export const schema = {
  $schema: "http://json-schema.org/draft-07/schema#",
  $ref: "#/definitions/NPMTokenRotationConfig",
  definitions: {
    NPMTokenRotationConfig: {
      type: "object",
      properties: {
        npmLoginUsernameSecret: {
          $ref: "#/definitions/SecretDetail",
        },
        npmLoginPasswordSecret: {
          $ref: "#/definitions/SecretDetail",
        },
        npmOtpSeedSecret: {
          $ref: "#/definitions/SecretDetail",
        },
        npmAccessTokenSecrets: {
          $ref: "#/definitions/AccessTokenRotationConfig",
        },
      },
      required: [
        "npmLoginUsernameSecret",
        "npmLoginPasswordSecret",
        "npmOtpSeedSecret",
        "npmAccessTokenSecrets",
      ],
      additionalProperties: false,
    },
    SecretDetail: {
      type: "object",
      additionalProperties: false,
      properties: {
        roleArn: {
          type: "string",
        },
        arn: {
          type: "string",
        },
        secretKey: {
          type: "string",
        },
      },
      required: ["arn", "secretKey"],
    },
    AccessTokenRotationConfig: {
      type: "object",
      properties: {
        secrets: {
          type: "array",
          items: {
            $ref: "#/definitions/AccessTokenItem",
          },
        },
        alarmSubscriptions: {
          type: "array",
          items: {
            type: "string",
          },
        },
      },
      required: ["secrets", "alarmSubscriptions"],
      additionalProperties: false,
    },
    AccessTokenItem: {
      type: "object",
      additionalProperties: false,
      properties: {
        publishConfig: {
          anyOf: [
            {
              $ref: "#/definitions/TokenPublishCircleCIContextConfig",
            },
            {
              $ref: "#/definitions/TokenPublishCircleCIEnvironmentConfig",
            },
          ],
        },
        slackWebHookConfig: {
          $ref: "#/definitions/SecretDetail",
        },
        arn: {
          type: "string",
        },
        secretKey: {
          type: "string",
        },
      },
      required: ["arn", "publishConfig", "secretKey", "slackWebHookConfig"],
    },
    TokenPublishCircleCIContextConfig: {
      type: "object",
      properties: {
        type: {
          type: "string",
          const: "Context",
        },
        contextName: {
          type: "string",
        },
        slug: {
          type: "string",
        },
        variableName: {
          type: "string",
        },
        circleCiToken: {
          $ref: "#/definitions/SecretDetail",
        },
      },
      required: [
        "type",
        "contextName",
        "slug",
        "variableName",
        "circleCiToken",
      ],
      additionalProperties: false,
    },
    TokenPublishCircleCIEnvironmentConfig: {
      type: "object",
      properties: {
        type: {
          type: "string",
          const: "Environment",
        },
        slug: {
          type: "string",
        },
        projectName: {
          type: "string",
        },
        variableName: {
          type: "string",
        },
        circleCiToken: {
          $ref: "#/definitions/SecretDetail",
        },
      },
      required: [
        "type",
        "slug",
        "projectName",
        "variableName",
        "circleCiToken",
      ],
      additionalProperties: false,
    },
  },
};
