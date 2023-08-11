import { login as loginPage } from '../pages/login';
import { testUsername, testUserPassword } from './settings';

type Options = {
  username?: string;
  password?: string;
};

export const login = async (t: TestController, options: Options = {}) => {
  const { username = testUsername(), password = testUserPassword() } = options;
  await t
    .click(loginPage.loginButton)

  await t
    .typeText(loginPage.username, username)
    .typeText(loginPage.password, password)
    .click(loginPage.loginButton);

  // Wait for authorization to finish
  await t.wait(1000); // 1s
};
