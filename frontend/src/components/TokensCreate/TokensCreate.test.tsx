import { rest } from "msw";
import { setupServer } from "msw/node";

import TokensCreate from "./TokensCreate";

import urls from "@/api/urls";
import type * as apiHooks from "@/hooks/react-query";
import { createMockTokensResolver } from "@/mocks/resolvers";
import { renderWithMemoryRouter, screen, userEvent } from "@/utils/test-utils";

const mockServer = setupServer(rest.post(urls.tokens, createMockTokensResolver()));

const tokensMutationMock = vi.fn();

vi.mock("@/hooks/react-query", async (importOriginal) => {
  const original: typeof apiHooks = await importOriginal();
  return { ...original, useTokensCreateMutation: () => ({ mutateAsync: tokensMutationMock }) };
});

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
  expect(screen.getByRole("form", { name: /Generate new enrolment tokens/i })).toBeInTheDocument();
});

it("if not all required fields have been entered the submit button is disabled", async () => {
  renderWithMemoryRouter(<TokensCreate />);
  const amount = screen.getByLabelText(/Amount of tokens to generate/i);
  const expires = screen.getByLabelText(/Expiration time/i);
  expect(screen.getByRole("button", { name: /Generate tokens/i })).toBeDisabled();
  await userEvent.type(amount, "1");
  await userEvent.type(expires, "1 month");
  expect(screen.getByRole("button", { name: /Generate tokens/i })).toBeEnabled();
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

it("can generate enrolment tokens", async () => {
  renderWithMemoryRouter(<TokensCreate />);
  const amount = screen.getByLabelText(/Amount of tokens to generate/i);
  const expires = screen.getByLabelText(/Expiration time/i);
  expect(screen.getByRole("button", { name: /Generate tokens/i })).toBeDisabled();
  // can specify the number of tokens to generate
  await userEvent.type(amount, "1");
  // can specify the token expiration time (e.g. 1 week)
  await userEvent.type(expires, "1 week");
  await userEvent.click(screen.getByRole("button", { name: /Generate tokens/i }));
  expect(tokensMutationMock).toHaveBeenCalledTimes(1);
  expect(tokensMutationMock).toHaveBeenCalledWith({
    amount: 1,
    duration: "P7DT0H0M0S",
  });
});

it("does not display error message on blur if the value has not chagned", async () => {
  renderWithMemoryRouter(<TokensCreate />);
  const amount = screen.getByLabelText(/Amount of tokens to generate/i);
  await userEvent.type(amount, "{tab}");
  expect(amount).not.toHaveErrorMessage(/Error/i);
  // enter a value and then delete it
  await userEvent.type(amount, "1{backspace}");
  expect(amount).toHaveErrorMessage(/Error/i);
});
