import { screen } from '@testing-library/testcafe';
import { envUrl } from '../utils/settings';

export const event = {
  name: `Test event ${new Date().toUTCString()}`,
  shortDescription: "event for testing",
  description: "event for testing",
  capacity: '15',
  participants: 'Family',
  duration: '30',
};

export const eventAdd = {
  saveButton: screen.getByText(/Tallenna ja poistu|Save/i),
  name: screen.getByLabelText(/Nimi:|Name:/i),
  description: screen.getByLabelText('Description:'),
  shortDescription: screen.getByLabelText('Short description:'),
  project: screen.getByLabelText('Project:'),
  capacity: screen.getByLabelText('Capacity per occurrence:'),
  participants: screen.getByLabelText('Participants per invite:'),
  duration: screen.getByLabelText('Duration:'),
  readyForPublish: screen.getByLabelText('Ready for event group publishing'),
  eventGroup: screen.getByLabelText('Event group:'),
  
};

export const route = () => `${envUrl()}/admin/events/event`;
export const routeAdd = () => `${envUrl()}/admin/events/event/add`;
