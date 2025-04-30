import { rest } from "msw";
import { setupServer } from "msw/node";

import TokensCreate from "./TokensCreate";

import { createMockTokensResolver } from "@/mocks/resolvers";
import { apiUrls } from "@/utils/test-urls";
import { renderWithMemoryRouter, screen, userEvent } from "@/utils/test-utils";

const mockServer = setupServer(rest.post(apiUrls.tokens, createMockTokensResolver()));

beforeAll(() => {
  mockServer.listen();
});

afterEach(() => {
  mockServer.resetHandlers();
});

afterAll(() => {
  mockServer.close();
});

it("renders the form", async () => {
  renderWithMemoryRouter(<TokensCreate />);
  expect(screen.getByRole("form", { name: /Generate new enrollment tokens/i })).toBeInTheDocument();
});

it("if not all required fields have been entered the submit button is disabled", async () => {
  renderWithMemoryRouter(<TokensCreate />);
  const amount = screen.getByLabelText(/Amount of tokens to generate/i);
  const expires = screen.getByLabelText(/Expiration time/i);
  expect(screen.getByRole("button", { name: /Generate tokens/i })).toBeAriaDisabled();
  await userEvent.type(amount, "1");
  await userEvent.type(expires, "1 month");
  expect(screen.getByRole("button", { name: /Generate tokens/i })).not.toBeAriaDisabled();
});

it("displays an error for invalid expiration value", async () => {
  renderWithMemoryRouter(<TokensCreate />);
  const expires = screen.getByLabelText(/Expiration time/i);
  await userEvent.type(expires, "2");
  await userEvent.tab();
  expect(expires).toHaveErrorMessage(
    /Time unit must be a `string` type with a value of weeks, days, hours, and\/or minutes./i,
  );
});

it("does not display error message on blur if the value has not chagned", async () => {
  renderWithMemoryRouter(<TokensCreate />);
  const amount = screen.getByLabelText(/Amount of tokens to generate/i);
  await userEvent.type(amount, "{tab}");
  expect(amount).not.toHaveErrorMessage(/Please enter a valid number/i);
  // enter a value and then delete it
  await userEvent.type(amount, "1{backspace}");
  expect(amount).toHaveErrorMessage(/Please enter a valid number/i);
});
