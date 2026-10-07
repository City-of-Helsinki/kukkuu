import { Selector } from "testcafe";
import { screen } from "@testing-library/testcafe";
import { envUrl } from "../utils/settings";
import getDropdownOption from "../utils/getDropdownOption";
import getHelsinkiDateTime from "../utils/getHelsinkiDateTime";

export const eventGroup = {
  name: `Test event group ${new Date().toUTCString()}`,
  description: "event group for testing",
};
export const eventGroupList = {
  action: screen.getByLabelText(/Toiminto:|Action:/i),
  goButton: Selector("button").withText(/Suorita|Go/i),
  actionPublish: "Publish selected event groups",
};

export const eventGroupPublish = {
  registrationOpensAtDate: Selector(
    'input.vDateField[name^="registration_opens_at"]',
  ),
  registrationOpensAtTime: Selector(
    'input.vTimeField[name^="registration_opens_at"]',
  ),
  submitButton: Selector('input[name="apply"]'),
};

export const eventGroupAdd = {
  saveButton: screen.getByRole("button", {
    name: /Tallenna ja poistu|^Save$/i,
  }),
  name: screen.getByLabelText(/Nimi:|Name:/i),
  description: screen.getByLabelText("Description:"),
  shortDescription: screen.getByLabelText("Short description:"),
  project: screen.getByLabelText("Project:"),
};

export const route = (name: string) =>
  `${envUrl()}/admin/events/eventgroup/?q=${encodeURIComponent(name)}`;
export const routeAdd = () => `${envUrl()}/admin/events/eventgroup/add`;

// publish event group from the list view
export const publish = async (t: TestController) => {
  await t.navigateTo(route(eventGroup.name));

  // checkbox on event group row
  const selectCheckbox = Selector(".field-name_with_fallback")
    .withText(eventGroup.name)
    .parent("tr")
    .child(".action-checkbox")
    .child(".action-select");

  // select correct event group
  await t
    .click(selectCheckbox)
    .click(eventGroupList.action)
    .click(getDropdownOption(eventGroupList.actionPublish));

  await t.click(eventGroupList.goButton);

  // Now + 2h, so the server does not reject it as past:
  const twoHoursFromNow = new Date(Date.now() + 2 * 60 * 60 * 1000);
  const { date, time } = getHelsinkiDateTime(twoHoursFromNow);

  await t
    .typeText(eventGroupPublish.registrationOpensAtDate, date)
    .typeText(eventGroupPublish.registrationOpensAtTime, time)
    .click(eventGroupPublish.submitButton);
};

// fill add form for new event group
export const fillFormAdd = async (
  t: TestController,
  projectName: string | RegExp
) => {
  await t
    .click(eventGroupAdd.project)
    .click(getDropdownOption(projectName))
    .typeText(eventGroupAdd.name, eventGroup.name)
    .typeText(eventGroupAdd.description, eventGroup.description);
};

// create new event group
export const createNew = async (
  t: TestController,
  projectName: string | RegExp
) => {
  await t.navigateTo(routeAdd());

  await fillFormAdd(t, projectName);

  await t.click(eventGroupAdd.saveButton);
};
