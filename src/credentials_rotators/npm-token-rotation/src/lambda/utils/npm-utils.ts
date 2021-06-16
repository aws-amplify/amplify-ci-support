import TOTP from "totp-generator";
import axios from "axios";
export const generateOtp = (seed: string) => {
  return TOTP(seed, { digits: 6 });
};

export const createAccessToken = async (
  username: string,
  password: string,
  otpSeed: string
): Promise<string> => {
  const otp = generateOtp(otpSeed);
  const result = await axios.post(
    "https://registry.npmjs.org/-/npm/v1/tokens",
    {
      password,
    },
    {
      headers: {
        "content-type": "application/json",
        "npm-otp": otp,
      },
      auth: {
        username,
        password,
      },
    }
  );
  return result.data["token"];
};

export const deleteAccessToken = async (
  username: string,
  password: string,
  otpSeed: string,
  token: string
): Promise<boolean> => {
  const otp = generateOtp(otpSeed);
  const result = await axios.delete(
    `https://registry.npmjs.org/-/npm/v1/tokens/token/${token}`,
    {
      headers: {
        "content-type": "application/json",
        "npm-otp": otp,
      },
      auth: {
        username,
        password,
      },
    }
  );
  return result.status >= 200 && result.status < 300;
};

export const validateAccessToken = async (
  username: string,
  accessToken: string
): Promise<boolean> => {
  const result = await axios.get("https://registry.npmjs.org/-/npm/v1/user", {
    headers: {
      Authorization: `Bearer ${accessToken}`,
      "content-type": "application/json",
    },
  });
  return result.status >= 200 && result.status < 300;
};