import { login as loginPage } from '../pages/login';
import { testUsername, testUserPassword } from './settings';


// const givePermission = async (t: TestController) => {
//   // If the user is show a permission request page
//   if (await ssoLogin.permissionPage.exists) {
//     // Give permission
//     await t.click(ssoLogin.givePermissionButton);
//   }
// };

type Options = {
  username?: string;
  password?: string;
};

export const login = async (t: TestController, options: Options = {}) => {
  const { username = testUsername(), password = testUserPassword() } = options;
  await t
    .click(loginPage.loginButton)

  // select locale English
  // await selectLoginLanguage(t, ssoLogin.localeLanguage);

  await t
    .typeText(loginPage.username, username)
    .typeText(loginPage.password, password)
    .click(loginPage.loginButton);

  // await givePermission(t);

  // Wait for authorization to finish
  await t.wait(1000); // 1s
};
