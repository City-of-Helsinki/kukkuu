import { Selector } from 'testcafe';
import { screen } from '@testing-library/testcafe';
import { envUrl } from '../utils/settings';
import  getDropdownOption from '../utils/getDropdownOption';

export const eventGroup = {
  name: `testi ${new Date().toUTCString()}`,
  description: "Test event group",
  action: screen.getByLabelText(/Toiminto:|Action:/i),
  actionPublish: "Publish",
  goButton: screen.getByText(/Suorita valittu toiminto|Go/i),
};

export const eventGroupAdd = {
  saveButton: screen.getByText(/Tallenna ja poistu|Save/i),
  name: screen.getByLabelText(/Nimi:|Name:/i),
  description: screen.getByLabelText('Description:'),
  shortDescription: screen.getByLabelText('Short description:'),
  project: screen.getByLabelText('Project:'),
};

export const route = () => `${envUrl()}/admin/events/eventgroup`;
export const routeAdd = () => `${envUrl()}/admin/events/eventgroup/add`;


export const publish = async (t: TestController) => {
  await t.navigateTo(route());

  const selectCheckbox = Selector('.field-name').withText(eventGroup.name).parent('tr').child('.action-checkbox').child('.action-select');

  // select correct event group 
  await t
  .click(selectCheckbox)
  .click(eventGroup.action).click(getDropdownOption(eventGroup.actionPublish));

  // and publish it
  await t.click(eventGroup.goButton);
};
