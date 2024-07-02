import { screen } from "@testing-library/testcafe";
import { envUrl } from "../utils/settings";
import getDropdownOption from "../utils/getDropdownOption";

export const event = {
  name: `Test event ${new Date().toUTCString()}`,
  shortDescription: "event for testing",
  description: "event for testing",
  capacity: "15",
  participants: "Family",
  duration: "30",
};

export const eventAdd = {
  saveButton: screen.getByRole("button", {
    name: /Tallenna ja poistu|^Save$/i,
  }),
  name: screen.getByLabelText(/Nimi:|Name:/i),
  description: screen.getByLabelText("Description:"),
  shortDescription: screen.getByLabelText("Short description:"),
  project: screen.getByLabelText("Project:"),
  capacity: screen.getByLabelText("Capacity per occurrence:"),
  participants: screen.getByLabelText("Participants per invite:"),
  duration: screen.getByLabelText("Duration:"),
  readyForPublish: screen.getByLabelText("Ready for event group publishing"),
  eventGroup: screen.getByLabelText("Event group:"),
};

export const route = () => `${envUrl()}/admin/events/event`;
export const routeAdd = () => `${envUrl()}/admin/events/event/add`;

// fill add form for new event
export const fillFormAdd = async (
  t: TestController,
  projectName: string | RegExp,
  eventGroupName: string
) => {
  const eventGroupOption = eventAdd.eventGroup.find("option");
  const eventGroupRegexp = new RegExp(eventGroupName, "i");

  await t
    .click(eventAdd.project)
    .click(getDropdownOption(projectName))
    .typeText(eventAdd.name, event.name)
    .typeText(eventAdd.shortDescription, event.shortDescription)
    .typeText(eventAdd.description, event.description)
    .typeText(eventAdd.capacity, event.capacity)
    .click(eventAdd.participants)
    .click(getDropdownOption(event.participants))
    .typeText(eventAdd.duration, event.duration)
    .click(eventAdd.readyForPublish)
    .click(eventAdd.eventGroup)
    .click(eventGroupOption.withText(eventGroupRegexp));
};

// create new event
export const createNew = async (
  t: TestController,
  projectName: string | RegExp,
  eventGroupName: string
) => {
  await t.navigateTo(routeAdd());

  await fillFormAdd(t, projectName, eventGroupName);

  await t.click(eventAdd.saveButton);
};
