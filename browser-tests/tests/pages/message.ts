import { screen } from "@testing-library/testcafe";
import { envUrl } from "../utils/settings";
import getDropdownOption from "../utils/getDropdownOption";

export const message = {
  subject: `Message  ${new Date().toUTCString()}`,
  body: "Message for testing",
  recipientSelection: "all",
};

export const messageAdd = {
  saveButton: screen.getByRole("button", {
    name: /Tallenna ja poistu|^Save$/i,
  }),
  subject: screen.getByLabelText("Subject:"),
  body: screen.getByLabelText("Body plain text:"),
  project: screen.getByLabelText("Project:"),
  recipientSelection: screen.getByLabelText("Recipient selection:"),
  event: screen.getByLabelText("Event:"),
};

export const route = () => `${envUrl()}/admin/messaging/message/`;
export const routeAdd = () => `${envUrl()}/admin/messaging/message/add/`;

// fill add form for new message
export const fillFormAdd = async (
  t: TestController,
  projectName: string,
  eventName: string
) => {
  const eventOption = messageAdd.event.find("option");
  const eventRegexp = new RegExp(eventName, "i");

  await t
    .click(messageAdd.project)
    .click(getDropdownOption(projectName))
    .typeText(messageAdd.subject, message.subject)
    .typeText(messageAdd.body, message.body)
    .click(messageAdd.recipientSelection)
    .click(
      messageAdd.recipientSelection
        .find("option")
        .withAttribute("value", message.recipientSelection)
    )
    .click(messageAdd.event)
    .click(eventOption.withText(eventRegexp));
};

// create new message
export const createNewMessage = async (
  t: TestController,
  projectName: string,
  eventName: string
) => {
  await t.navigateTo(routeAdd());

  await fillFormAdd(t, projectName, eventName);

  await t.click(messageAdd.saveButton);
};
