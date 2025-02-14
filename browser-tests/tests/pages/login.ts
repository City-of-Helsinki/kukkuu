import { screen } from '@testing-library/testcafe';

export const login = {
  loginButton: screen.getByRole('button', { name: /Kirjaudu sisään|Log in/i }),
  username: screen.getByLabelText(/Käyttäjätunnus:|Username:/i),
  password: screen.getByLabelText(/Salasana:|Password:/i),
};
