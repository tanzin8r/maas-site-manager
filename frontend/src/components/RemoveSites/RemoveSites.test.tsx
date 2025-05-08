import { http, HttpResponse } from "msw";

import RemoveSites from "./RemoveSites";

import { siteFactory, statsFactory } from "@/mocks/factories";
import { sitesResolvers } from "@/testing/resolvers/sites";
import { apiUrls } from "@/utils/test-urls";
import { screen, setupServer, render, userEvent } from "@/utils/test-utils";

const stats = statsFactory.build();
const site = siteFactory.build({ stats });

const mockServer = setupServer(sitesResolvers.getSite.handler([site]));
const errorMessage = /Confirmation string is not correct/i;

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
    useRowSelection: () => ({
      rowSelection: {
        "1": true,
        "2": true,
      },
    }),
  };
});

it("enables the submit button when something has been typed", async () => {
  render(<RemoveSites />);

  expect(screen.getByRole("button", { name: /Remove/i })).toBeAriaDisabled();

  await userEvent.type(screen.getByRole("textbox"), "invalid text");

  expect(screen.queryByText(errorMessage)).not.toBeInTheDocument();
  expect(screen.getByRole("button", { name: /Remove/i })).not.toBeAriaDisabled();
});

it("shows validation errors after user attempts submission", async () => {
  render(<RemoveSites />);

  await userEvent.type(screen.getByRole("textbox"), "incorrect string{tab}");

  expect(screen.queryByText(errorMessage)).not.toBeInTheDocument();

  await userEvent.click(screen.getByRole("button", { name: /Remove/i }));

  expect(screen.getByText(errorMessage)).toBeInTheDocument();
});

it("does not display error message on blur if the value has not chagned", async () => {
  render(<RemoveSites />);

  expect(screen.getByRole("button", { name: /Remove/i })).toBeAriaDisabled();

  await userEvent.type(screen.getByRole("textbox"), "{tab}");

  expect(screen.queryByText(errorMessage)).not.toBeInTheDocument();
  expect(screen.getByRole("button", { name: /Remove/i })).toBeAriaDisabled();
});

it("hides validation errors on change if the user already attempted submission", async () => {
  render(<RemoveSites />);

  await userEvent.type(screen.getByRole("textbox"), "incorrect string");
  await userEvent.click(screen.getByRole("button", { name: /Remove/i }));

  expect(screen.getByText(errorMessage)).toBeInTheDocument();

  await userEvent.clear(screen.getByRole("textbox"));
  await userEvent.type(screen.getByRole("textbox"), "remove 2 sites");

  expect(screen.queryByText(errorMessage)).not.toBeInTheDocument();
});

it("shows error messages from the backend after submission", async () => {
  mockServer.use(
    http.delete(apiUrls.sites, () => {
      return new HttpResponse(null, { status: 400 });
    }),
  );

  render(<RemoveSites />);

  await userEvent.type(screen.getByRole("textbox"), "remove 2 sites");
  await userEvent.click(screen.getByRole("button", { name: /Remove/i }));

  expect(await screen.findByText(/Error while deleting sites/i)).toBeInTheDocument();
});
