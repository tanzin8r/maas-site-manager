import { rest } from "msw";

import MaasImages from "./MaasImages";

import { createMockGetSettingsResolver, createMockPatchSettingsResolver } from "@/mocks/resolvers";
import { apiUrls } from "@/utils/test-urls";
import { renderWithMemoryRouter, screen, setupServer, userEvent, waitFor } from "@/utils/test-utils";

const initialHandlers = [
  rest.get(apiUrls.settings, createMockGetSettingsResolver()),
  rest.patch(apiUrls.settings, createMockPatchSettingsResolver()),
];
const mockServer = setupServer(...initialHandlers);

beforeAll(() => {
  mockServer.listen();
});

afterEach(() => {
  mockServer.resetHandlers(...initialHandlers);
  localStorage.clear();
});

afterAll(() => {
  mockServer.close();
});

it("displays a form", () => {
  renderWithMemoryRouter(<MaasImages />);

  expect(screen.getByRole("form", { name: "maas.io" })).toBeInTheDocument();
});

it("disables inputs when loading", async () => {
  mockServer.resetHandlers(
    rest.get(apiUrls.settings, (req, res, ctx) => {
      return res(ctx.delay(Infinity));
    }),
  );
  renderWithMemoryRouter(<MaasImages />);
  const checkboxInput = screen.getByRole("checkbox", {
    name: "Connect to maas.io and keep selected images up to date.",
  });
  expect(checkboxInput).toBeAriaDisabled();
  expect(screen.getByRole("button", { name: "Save" })).toBeAriaDisabled();
});

it("enables the 'Save' button once there are changes", async () => {
  renderWithMemoryRouter(<MaasImages />);
  const checkboxInput = screen.getByRole("checkbox", {
    name: "Connect to maas.io and keep selected images up to date.",
  });
  await waitFor(() => expect(checkboxInput).toBeChecked());
  const saveButton = screen.getByRole("button", { name: "Save" });
  expect(saveButton).toBeAriaDisabled();
  await userEvent.click(checkboxInput);
  await waitFor(() => expect(saveButton).not.toBeAriaDisabled());
  await userEvent.click(checkboxInput);
  expect(saveButton).toBeAriaDisabled();
});
