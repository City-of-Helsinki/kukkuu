import { screen } from '@testing-library/testcafe';
import { envUrl } from '../utils/settings';

export const message = {
  subject: `Message  ${new Date().toUTCString()}`,
  body: "Message for testing",
  recipientSelection: 'all',
};

export const messageAdd = {
  saveButton: screen.getByText(/Tallenna ja poistu|Save/i),
  subject: screen.getByLabelText('Subject:'),
  body: screen.getByLabelText('Body plain text:'),
  project: screen.getByLabelText('Project:'),
  recipientSelection: screen.getByLabelText('Recipient selection:'),
  event: screen.getByLabelText('Event:'),
};

export const route = () => `${envUrl()}/admin/messaging/message/`;
export const routeAdd = () => `${envUrl()}/admin/messaging/message/add/`;
