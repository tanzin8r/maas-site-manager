import { rest } from "msw";

import RemoveSites from "./RemoveSites";

import { siteFactory, statsFactory } from "@/mocks/factories";
import { createMockSiteResolver } from "@/mocks/resolvers";
import { apiUrls } from "@/utils/test-urls";
import { screen, setupServer, render, userEvent } from "@/utils/test-utils";

const stats = statsFactory.build();
const site = siteFactory.build({ stats });

const mockServer = setupServer(rest.get(`${apiUrls.sites}/:id`, createMockSiteResolver([site])));

beforeAll(() => {
  mockServer.listen();
});

afterEach(() => {
  mockServer.resetHandlers();
});

afterAll(() => {
  mockServer.close();
});

beforeAll(() => {
  mockServer.listen();
});
afterEach(() => {
  mockServer.resetHandlers();
  localStorage.clear();
});
afterAll(() => {
  mockServer.close();
});

vi.mock("@/context", async () => {
  const actual = await vi.importActual("@/context");
  return {
    ...actual!,
    useRowSelectionContext: () => ({
      rowSelection: {
        "1": true,
        "2": true,
      },
    }),
  };
});

it("submit button should not be disabled when something has been typed", async () => {
  render(<RemoveSites />);
  const errorMessage = /Confirmation string is not correct/i;
  expect(screen.getByRole("button", { name: /Remove/i })).toBeDisabled();
  await userEvent.type(screen.getByRole("textbox"), "invalid text");
  expect(screen.queryByText(errorMessage)).not.toBeInTheDocument();
  expect(screen.getByRole("button", { name: /Remove/i })).toBeEnabled();
});

it("validation error is shown after user attempts submission", async () => {
  render(<RemoveSites />);
  const errorMessage = /Confirmation string is not correct/i;
  await userEvent.type(screen.getByRole("textbox"), "incorrect string{tab}");
  expect(screen.queryByText(errorMessage)).not.toBeInTheDocument();
  await userEvent.click(screen.getByRole("button", { name: /Remove/i }));
  expect(screen.getByText(errorMessage)).toBeInTheDocument();
});

it("does not display error message on blur if the value has not chagned", async () => {
  render(<RemoveSites />);
  expect(screen.getByRole("button", { name: /Remove/i })).toBeDisabled();
  await userEvent.type(screen.getByRole("textbox"), "{tab}");
  expect(screen.queryByText(/Confirmation string is not correct/i)).not.toBeInTheDocument();
  expect(screen.getByRole("button", { name: /Remove/i })).toBeDisabled();
});

it("validation error is hidden on change if the user already attempted submission", async () => {
  render(<RemoveSites />);
  const errorMessage = /Confirmation string is not correct/i;
  await userEvent.type(screen.getByRole("textbox"), "incorrect string");
  await userEvent.click(screen.getByRole("button", { name: /Remove/i }));
  expect(screen.getByText(errorMessage)).toBeInTheDocument();
  await userEvent.clear(screen.getByRole("textbox"));
  await userEvent.type(screen.getByRole("textbox"), "remove 2 sites");
  expect(screen.queryByText(errorMessage)).not.toBeInTheDocument();
});
