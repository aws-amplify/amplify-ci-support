/// <reference types="jest" />
declare const AWS: any;
declare const axios: any;
declare const createAccessKeyMock: jest.Mock<
  {
    promise: () => {
      AccessKey: string;
    };
  },
  []
>;
declare const deleteAccessKeyMock: jest.Mock<
  {
    promise: () => true;
  },
  []
>;
declare const getRoleMock: jest.Mock<
  {
    promise: () => {
      Arn: string;
    };
  },
  []
>;
declare const secretsManagerMock: jest.Mock<
  {
    promise: () => {
      SecretString: string;
    };
  },
  []
>;
declare const handler: any;
declare const data: {
  data: {
    items: {
      id: number;
      name: string;
    }[];
  };
};
