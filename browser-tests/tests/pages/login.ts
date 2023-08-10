import { screen } from '@testing-library/testcafe';

export const login = {
  loginButton: screen.getByText('Log in'),
  username: screen.getByLabelText('Username:'),
  password: screen.getByLabelText('Password:'),
};
