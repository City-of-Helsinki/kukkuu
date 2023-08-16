import { Selector } from 'testcafe';
import { screen } from '@testing-library/testcafe';
import { envUrl } from '../utils/settings';

const year = new Date().getFullYear();

export const project = {
  name: "Testi",
  year: year.toString(),
  selectByYear: Selector('tr').withText(year.toString()),
};
export const projectAdd = {
  saveButton: screen.getByText(/Tallenna ja poistu|Save/i),
  name: screen.getByLabelText(/Nimi:|Name:/i),
  year: screen.getByLabelText('Year:'),
};

export const route = () => `${envUrl()}/admin/projects/project/`;
export const routeAdd = () => `${envUrl()}/admin/projects/project/add/`;

export const addProject = async (t: TestController) => {
  await t.navigateTo(routeAdd());

  await t
    .typeText(projectAdd.name, project.name)
    .typeText(projectAdd.year, year.toString())
    .click(projectAdd.saveButton);
};

export const checkProject = async (t: TestController) => {
  await t.navigateTo(route());

  const eventGroupRow = project.selectByYear.child();
  
  if (await eventGroupRow.exists) {
    return;
  }

  // project did not found, create it
  // project should create only once
  await addProject(t);
};