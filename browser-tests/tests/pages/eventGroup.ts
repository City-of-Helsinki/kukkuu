import { Selector } from "testcafe";
import { screen } from "@testing-library/testcafe";
import { envUrl } from "../utils/settings";
import getDropdownOption from "../utils/getDropdownOption";

export const eventGroup = {
  name: `Test event group ${new Date().toUTCString()}`,
  description: "event group for testing",
};
export const eventGroupList = {
  action: screen.getByLabelText(/Toiminto:|Action:/i),
  goButton: Selector("button").withText(/Suorita|Go/i),
  actionPublish: "Publish",
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

export const route = () => `${envUrl()}/admin/events/eventgroup`;
export const routeAdd = () => `${envUrl()}/admin/events/eventgroup/add`;

// publish event group from the list view
export const publish = async (t: TestController) => {
  await t.navigateTo(route());

  // checkbox on event group row
  const selectCheckbox = Selector(".field-name")
    .withText(eventGroup.name)
    .parent("tr")
    .child(".action-checkbox")
    .child(".action-select");

  // select correct event group
  await t
    .click(selectCheckbox)
    .click(eventGroupList.action)
    .click(getDropdownOption(eventGroupList.actionPublish));

  // and publish it
  await t.click(eventGroupList.goButton);
};

// fill add form for new event group
export const fillFormAdd = async (t: TestController, projectName: string) => {
  await t
    .click(eventGroupAdd.project)
    .click(getDropdownOption(projectName))
    .typeText(eventGroupAdd.name, eventGroup.name)
    .typeText(eventGroupAdd.description, eventGroup.description);
};

// create new event group
export const createNew = async (t: TestController, projectName: string) => {
  await t.navigateTo(routeAdd());

  await fillFormAdd(t, projectName);

  await t.click(eventGroupAdd.saveButton);
};
