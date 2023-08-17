import {
  testUsername,
  testUserPassword,
} from './utils/settings';

import {
  event,
  createNew as createNewEvent
} from './pages/event';
import {
  createNew as createNewOccurence,
} from './pages/occurence';
import {
  eventGroup,
  publish as publishEventGroup,
  createNew as createNewEventGroup
} from './pages/eventGroup';
import {
  projectExists,
  project,
} from './pages/project';
import {
  venue,
  venueExists,
} from './pages/venue';

import { createNewMessage } from './pages/message';
import { userExists } from './pages/user';
import { route as routeHome } from './pages/home';

import { login } from './utils/login';

fixture`Event group feature`
  .page(routeHome())
  .beforeEach(async (t) => {
    await login(t, {
      username: testUsername(),
      password: testUserPassword(),
    });
    await t.wait(1000);

    await projectExists(t);
    await venueExists(t);
  });

test('Add initial data for ui and admin ui tests', async (t) => {
  const projectName = `${project.name} ${project.year}`;

  // add new event group
  await createNewEventGroup(t, projectName);

  // add new event
  await createNewEvent(t, projectName, eventGroup.name);

  // add new occurence
  await createNewOccurence(t, event.name, venue.name);

  // add new message
  await createNewMessage(t, projectName, event.name);

  // publish event group, event and occurence
  await publishEventGroup(t);

  // check ui user exists
  await userExists(t);
});
