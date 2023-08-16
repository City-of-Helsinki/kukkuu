import { Selector } from 'testcafe';
import { screen } from '@testing-library/testcafe';
import  getDropdownOption from '../utils/getDropdownOption';
import { envUrl } from '../utils/settings';
import { project} from '../pages/project';

const venueName = "Testila";

export const venue = {
  name: venueName,
  description: "Venue for testing",
  selectByName: Selector('tr').withText(venueName),
};
export const venueAdd = {
  saveButton: screen.getByText(/Tallenna ja poistu|Save/i),
  project: screen.getByLabelText('Project:'),
  name: screen.getByLabelText(/Nimi:|Name:/i),
  description: screen.getByLabelText('Description:'),
};

export const route = () => `${envUrl()}/admin/venues/venue/`;
export const routeAdd = () => `${envUrl()}/admin/venues/venue/add/`;

export const addVenue = async (t: TestController) => {
  await t.navigateTo(routeAdd());

  await t
    .click(venueAdd.project).click(getDropdownOption(`${project.name} ${project.year}`))
    .typeText(venueAdd.name, venue.name)
    .typeText(venueAdd.description, venue.description)
    .click(venueAdd.saveButton);
};

export const checkVenue = async (t: TestController) => {
  await t.navigateTo(route());

  const venueRow = venue.selectByName.child();
  
  if (await venueRow.exists) {
    return;
  }

  // venue did not found, create it
  // venue needs to create only once
  await addVenue(t);
};