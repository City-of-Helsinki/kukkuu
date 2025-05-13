// @ts-ignore
import * as dotenv from 'dotenv';

// eslint-disable-next-line @typescript-eslint/no-require-imports, @typescript-eslint/no-var-requires
const get = require('lodash/get');

dotenv.config();

function getOrError(variableName: string) {
  const variable = get(process.env, variableName);

  if (!variable) {
    throw new Error(`No ${variableName} specified.`);
  }

  return variable;
}

const getApiBaseUrl = (url: string) => {
  // API url might point to graphql, remove it from url
  var re = /\/graphql$/;
  return url.replace(re, "");
};


export const testUsername = (): string => getOrError('BROWSER_TESTS_API_ADMIN_USER_NAME');

export const testUserPassword = (): string => getOrError('BROWSER_TESTS_API_ADMIN_PASSWORD');

export const envUrl = (): string => getApiBaseUrl(getOrError('BROWSER_TESTS_API_URL'));

export const testUiUsername = (): string => getOrError('BROWSER_TESTS_USER_NAME');

export const testUiUserPassword = (): string => getOrError('BROWSER_TESTS_USER_PASSWORD');
