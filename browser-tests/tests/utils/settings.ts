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

export const testUsername = (): string => getOrError('BROWSER_TESTS_UID');

export const testUserPassword = (): string => getOrError('BROWSER_TESTS_PWD');

export const envUrl = (): string => getOrError('BROWSER_TESTS_ENV_URL');

export const testUiUsername = (): string => getOrError('BROWSER_TESTS_USERNAME_UI');

export const testUiUserPassword = (): string => getOrError('BROWSER_TESTS_PASSWORD_UI');


export const testUnauthorizedUsername = (): string =>
  getOrError('BROWSER_TESTS_UNAUTHORIZED_UID');

export const testUnauthorizedUserPassword = (): string =>
  getOrError('BROWSER_TESTS_UNAUTHORIZED_PWD');

