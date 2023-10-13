import { Selector } from "testcafe";
import { screen } from "@testing-library/testcafe";
import { envUrl, testUiUsername, testUiUserPassword } from "../utils/settings";

export const user = {
  username: `${testUiUsername()}`,
  password: `${testUiUserPassword()}`,
};

export const userList = {
  selectByUsername: Selector("tr").withText(`${testUiUsername()}`),
  selectByEmail: Selector(".field-email")
    .withText(`${testUiUsername()}`)
    .sibling(".field-username")
    .child("a"),
};

export const userAdd = {
  saveButton: screen.getByRole("button", {
    name: /Tallenna ja poistu|^Save$/i,
  }),
  username: screen.getByLabelText(/Käyttäjätunnus:|Username:/i),
  password: screen.getByLabelText(/Salasana:|Password:/i),
  passwordConfirmation: screen.getByLabelText(
    /Salasanan vahvistaminen:|Password confirmation:/i
  ),
  // user change
  staffStatus: screen.getByLabelText(/Ylläpitäjä|Staff status/i),
  staffStatusCheckbox: Selector("#id_is_staff"),
  superUserStatus: screen.getByLabelText(/Pääkäyttäjä|Superuser status/i),
  superUserStatusCheckbox: Selector("#id_is_superuser"),
  chooseAllPermissions: Selector("#id_user_permissions_add_all_link"),
};

export const route = () => `${envUrl()}/admin/users/user/`;
export const routeAdd = () => `${envUrl()}/admin/users/user/add/`;

export const addUser = async (t: TestController) => {
  await t.navigateTo(routeAdd());

  // username & password page
  await t
    .typeText(userAdd.username, user.username)
    .typeText(userAdd.password, user.password)
    .typeText(userAdd.passwordConfirmation, user.password)
    .click(userAdd.saveButton);

  // user details page
  await t
    .click(userAdd.staffStatus)
    .click(userAdd.superUserStatus)
    .click(userAdd.chooseAllPermissions)
    .click(userAdd.saveButton);
};

export const tunnistamoUser = async (t: TestController) => {
  await t.navigateTo(route());

  await t.click(userList.selectByEmail);

  // these needs to be checked
  if (!(await userAdd.staffStatusCheckbox.checked)) {
    await t.click(userAdd.staffStatus);
  }
  if (!(await userAdd.superUserStatusCheckbox.checked)) {
    await t.click(userAdd.superUserStatus);
  }

  await t.click(userAdd.chooseAllPermissions).click(userAdd.saveButton);
};

export const userExists = async (t: TestController) => {
  await t.navigateTo(route());

  const userRow = userList.selectByUsername.child();

  if (await userRow.exists) {
    // tunnistamo user accesses are checked on ui and admin test sets
    // await tunnistamoUser(t);
    return;
  }

  // user did not exists, create it
  // user should create only once
  await addUser(t);
};
