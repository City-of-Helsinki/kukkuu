import { screen } from '@testing-library/testcafe';
import {
  testUsername,
  testUserPassword,
} from './utils/settings';

import  getDropdownOption from './utils/getDropdownOption';

import {
  event,
  eventAdd,
  routeAdd as routeEventAdd,
} from './pages/event';
import {
  eventGroup,
  eventGroupAdd,
  routeAdd as routeEventGroupAdd,
} from './pages/eventGroup';
import {
  message,
  messageAdd,
  routeAdd as routeMessageAdd,
} from './pages/message';
import {
  checkProject,
  project,
} from './pages/project';


import {
  user,
  userExists,
  routeAdd as routeUserAdd,
} from './pages/user';

import { login } from './utils/login';

fixture`Event group feature`
  .page(routeEventGroupAdd())
  .beforeEach(async (t) => {
    await login(t, {
      username: testUsername(),
      password: testUserPassword(),
    });
    await t.wait(3000);

    await checkProject(t); 
  });

test('Add initial data for ui and admin ui tests', async (t) => {
  // add event group
  await t.navigateTo(routeEventGroupAdd());

  await t
  .click(eventGroupAdd.project).click(getDropdownOption(`${project.name} ${project.year}`))
  .typeText(eventGroupAdd.name, eventGroup.name)
  .typeText(eventGroupAdd.description, eventGroup.description);

  await t
  .click(eventGroupAdd.saveButton);

  // add event
  await t.navigateTo(routeEventAdd());

  await t
  .click(eventAdd.project).click(getDropdownOption(`${project.name} ${project.year}`))
  .typeText(eventAdd.name, event.name)
  .typeText(eventAdd.shortDescription, event.shortDescription)
  .typeText(eventAdd.description, event.description)
  .typeText(eventAdd.capacity, event.capacity)
  .click(eventAdd.participants).click(getDropdownOption(event.participants))
  .typeText(eventAdd.duration, event.duration)
  .click(eventAdd.readyForPublish)
  .click(eventGroupAdd.saveButton);

  // add message
  await t.navigateTo(routeMessageAdd());

  const eventOption = messageAdd.event.find('option');
  const eventRegexp = new RegExp(event.name, "i");

  await t
  .click(messageAdd.project).click(getDropdownOption(`${project.name} ${project.year}`))
  .typeText(messageAdd.subject, message.subject)
  .typeText(messageAdd.body, message.body)
  .click(messageAdd.recipientSelection).click(getDropdownOption(message.recipientSelection))
  .click(messageAdd.event).click(eventOption.withText(eventRegexp))
  .click(eventGroupAdd.saveButton);

  // check ui user exists
  await userExists(t); 
});
