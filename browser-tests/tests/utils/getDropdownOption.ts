import { screen } from "@testing-library/testcafe";

function getDropdownOption(label: string | RegExp) {
  return screen.getByRole("option", { name: label });
}

export default getDropdownOption;
