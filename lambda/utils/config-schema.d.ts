export declare const schema: {
  $schema: string;
  $ref: string;
  definitions: {
    E2eTokenRotationConfig: {
      type: string;
      properties: {
        circleCiToken: {
          $ref: string;
        };
        alarmSubscriptions: {
          type: string;
          items: {
            type: string;
          };
        };
        circleCiConfigs: {
          type: string;
          items: {
            type: string;
            properties: {
              type: {
                type: string;
                const: string;
              };
              name: {
                type: string;
              };
              slug: {
                type: string;
              };
              secretKeyIdVariableName: {
                type: string;
              };
              secretKeyVariableName: {
                type: string;
              };
              sessionTokenVariableName: {
                type: string;
              };
              roleName: {
                type: string;
              };
              permissions: {
                type: string;
                items: {
                  type: string;
                  properties: {
                    resources: {
                      type: string;
                      items: {
                        type: string;
                      };
                    };
                    actions: {
                      type: string;
                      items: {
                        type: string;
                      };
                    };
                    effect: {
                      type: string;
                    };
                  };
                  required: string[];
                  additionalProperties: boolean;
                };
              };
            };
            required: string[];
            additionalProperties: boolean;
          };
        };
      };
      required: string[];
      additionalProperties: boolean;
    };
    SecretDetail: {
      type: string;
      properties: {
        arn: {
          type: string;
        };
        secretKey: {
          type: string;
        };
      };
      required: string[];
      additionalProperties: boolean;
    };
  };
};
