import TOTP from "totp-generator";
import axios from "axios";
import { URL } from "url";
import assert from 'assert';

export const generateOtp = (otpUrl: string) => {
  let seed;
  if (otpUrl.startsWith("otpauth")) {
    const url = new URL(otpUrl);
    seed = url.searchParams.get("secret");
    assert(seed, "OTP URL is missing secret parameter");
  } else {
    seed = otpUrl;
  }
  return TOTP(seed, { digits: 6 });
};

export const createAccessToken = async (
  username: string,
  password: string,
  otpSeed: string
): Promise<string> => {
  try {
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
  } catch (e) {
    throw new Error(`Error occurred when creating token: ${e.message}`);
  }
};

export const deleteAccessToken = async (
  username: string,
  password: string,
  otpSeed: string,
  token: string
): Promise<boolean> => {
  try {
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
  } catch (e) {
    throw new Error(`Error occurred when deleting token: ${e.message}`);
  }
};

export const validateAccessToken = async (
  username: string,
  accessToken: string
): Promise<boolean> => {
  try {
    const result = await axios.get("https://registry.npmjs.org/-/npm/v1/user", {
      headers: {
        Authorization: `Bearer ${accessToken}`,
        "content-type": "application/json",
      },
    });
    return result.status >= 200 && result.status < 300;
  } catch (e) {
    throw new Error(`Error occurred when verifying token: ${e.message}`);
  }
};
