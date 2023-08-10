import { screen } from '@testing-library/testcafe';
import { envUrl } from '../utils/settings';

export const eventGroup = {
  name: `testi  ${new Date().toUTCString()}`,
  description: "Test event group",
};

export const eventGroupAdd = {
  saveButton: screen.getByText('Save'),
  name: screen.getByLabelText('Name:'),
  description: screen.getByLabelText('Description:'),
  shortDescription: screen.getByLabelText('Short description:'),
  project: screen.getByLabelText('Project:'),
};

export const route = () => `${envUrl()}/admin/events/eventgroup`;
export const routeAdd = () => `${envUrl()}/admin/events/eventgroup/add`;
