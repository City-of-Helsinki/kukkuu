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
  checkProject,
  project,
} from './pages/project';
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

test('As a admin user I want to add event and event group', async (t) => {
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
});
