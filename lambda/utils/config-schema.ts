// Schema is automatically generated using Name: Typescript JSON schema generator using
// https://marketplace.visualstudio.com/items?itemName=marcoq.vscode-typescript-to-json-schema
// the input type for the schema is in ../../src/stacks/types.ts

export const schema = {
  $schema: "http://json-schema.org/draft-07/schema#",
  $ref: "#/definitions/E2eTokenRotationConfig",
  definitions: {
    E2eTokenRotationConfig: {
      type: "object",
      properties: {
        circleCiToken: {
          $ref: "#/definitions/SecretDetail"
        },
        alarmSubscriptions: {
          type: "array",
          items: {
            type: "string"
          }
        },
        circleCiConfigs: {
          type: "array",
          items: {
            type: "object",
            properties: {
              type: {
                type: "string",
                const: "Context"
              },
              name: {
                type: "string"
              },
              slug: {
                type: "string"
              },
              secretKeyIdVariableName: {
                type: "string"
              },
              secretKeyVariableName: {
                type: "string"
              },
              sessionTokenVariableName: {
                type: "string"
              },
              roleName: {
                type: "string"
              },
              permissions: {
                type: "array",
                items: {
                  type: "object",
                  properties: {
                    resources: {
                      type: "array",
                      items: {
                        type: "string"
                      }
                    },
                    actions: {
                      type: "array",
                      items: {
                        type: "string"
                      }
                    },
                    effect: {
                      type: "string"
                    }
                  },
                  required: ["effect", "actions", "resources"],
                  additionalProperties: false
                }
              }
            },
            required: [
              "type",
              "name",
              "slug",
              "secretKeyIdVariableName",
              "secretKeyVariableName",
              "sessionTokenVariableName"
            ],
            additionalProperties: false
          }
        }
      },
      required: ["circleCiToken", "alarmSubscriptions", "circleCiConfigs"],
      additionalProperties: false
    },
    SecretDetail: {
      type: "object",
      properties: {
        arn: {
          type: "string"
        },
        secretKey: {
          type: "string"
        }
      },
      required: ["arn", "secretKey"],
      additionalProperties: false
    }
  }
};
