import { screen } from '@testing-library/testcafe';
import { envUrl } from '../utils/settings';
import { Selector } from 'testcafe';

export const occurence = {
  name: `Event  ${new Date().toUTCString()}`,
  shortDescription: "event for testing",
  description: "event for testing",
  capacity: '10',
};

export const occurenceAdd = {
  saveButton: screen.getByText('Save'),
  todayLink: Selector('a').withText('Today'),
  nowLink: Selector('a').withText('Now'),
  date: Selector('p').withText('Date:'),
  event: screen.getByLabelText('Event:'),
  venue: screen.getByLabelText('Venue:'),
  capacityOverride: screen.getByLabelText('Capacity override:'),
};

export const route = () => `${envUrl()}/admin/events/occurrence`;
export const routeAdd = () => `${envUrl()}/admin/events/occurrence/add`;

export const fillFormAdd = async (t: TestController, eventName: string, venueName: string) => {
  const eventOption = occurenceAdd.event.find('option');
  const eventRegexp = new RegExp(eventName, "i");

  const venueOption = occurenceAdd.venue.find('option');
  const venueRegexp = new RegExp(venueName, "i");
  const today = new Date();

  await t
  // .click(occurenceAdd.todayLink)
  .typeText(occurenceAdd.date, `${today.getFullYear()+1}-${today.getMonth()}-${today.getDate()}` )
  .click(occurenceAdd.nowLink)
  .click(occurenceAdd.event).click(eventOption.withText(eventRegexp))
  .click(occurenceAdd.venue).click(venueOption.withText(venueRegexp))
  .typeText(occurenceAdd.capacityOverride, occurence.capacity);
};

export const createNewOccurence = async (t: TestController, eventName: string, venueName: string) => {
  await t.navigateTo(routeAdd());

  await fillFormAdd(t, eventName, venueName);

  await t.click(occurenceAdd.saveButton);
};
