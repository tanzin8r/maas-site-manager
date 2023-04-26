import { waitFor } from "@testing-library/react";
import { rest } from "msw";
import { setupServer } from "msw/node";

import TokensList from "./TokensList";

import urls from "@/api/urls";
import { tokenFactory } from "@/mocks/factories";
import { createMockDeleteTokensResolver, createMockGetTokensResolver } from "@/mocks/resolvers";
import { screen, renderWithMemoryRouter, within, userEvent } from "@/test-utils";

const tokens = tokenFactory.buildList(2);
const mockServer = setupServer(
  rest.get(urls.tokens, createMockGetTokensResolver(tokens)),
  rest.delete(urls.tokens, createMockDeleteTokensResolver()),
);

beforeAll(() => {
  mockServer.listen();
});

afterEach(() => {
  mockServer.resetHandlers();
});

afterAll(() => {
  mockServer.close();
});

it("should display tokens table on mount with loading text", () => {
  renderWithMemoryRouter(<TokensList />);

  const tokensTable = screen.getByRole("table", { name: /tokens/i });
  expect(tokensTable).toBeInTheDocument();
  expect(within(tokensTable).getByText(/loading/i)).toBeInTheDocument();
});

it("should display table with tokens", async () => {
  renderWithMemoryRouter(<TokensList />);

  await waitFor(() => expect(screen.getAllByRole("rowgroup")).toHaveLength(2));
  const tableBody = screen.getAllByRole("rowgroup")[1];
  expect(within(tableBody).getAllByRole("row")).toHaveLength(tokens.length);
  within(tableBody)
    .getAllByRole("row")
    .forEach((row, idx) => expect(row).toHaveTextContent(new RegExp(tokens[idx].token, "i")));
});

it("should display a token count description", () => {
  renderWithMemoryRouter(<TokensList />);

  expect(screen.getByText(new RegExp(`showing 2 out of 2 tokens`, "i"))).toBeInTheDocument();
});

it("disables the Delete button if no rows are selected", async () => {
  renderWithMemoryRouter(<TokensList />);

  expect(screen.getByRole("button", { name: "Delete" })).toBeDisabled();

  await userEvent.click(screen.getAllByRole("checkbox")[0]);

  expect(screen.getByRole("button", { name: "Delete" })).not.toBeDisabled();
});

it("disables the Export button if no rows are selected", async () => {
  renderWithMemoryRouter(<TokensList />);

  expect(screen.getByRole("button", { name: "Export" })).toBeDisabled();

  await userEvent.click(screen.getAllByRole("checkbox")[0]);

  expect(screen.getByRole("button", { name: "Export" })).not.toBeDisabled();
});

it("displays a notification after a successful single deletion", async () => {
  renderWithMemoryRouter(<TokensList />);

  await userEvent.click(screen.getAllByRole("checkbox")[1]);
  await userEvent.click(screen.getByRole("button", { name: /delete/i }));

  expect(
    screen.getByRole("heading", {
      name: /deleted/i,
    }),
  ).toBeInTheDocument();
  expect(screen.getByText(/an enrollment token was deleted\./i)).toBeInTheDocument();
});

it("display a different notification for multiple deletions", async () => {
  renderWithMemoryRouter(<TokensList />);
  const checkboxes = screen.getAllByRole("checkbox");
  await userEvent.click(checkboxes[1]);
  await userEvent.click(checkboxes[2]);
  await userEvent.click(screen.getByRole("button", { name: /delete/i }));

  expect(screen.getByText(/2 enrollment tokens were deleted\./i)).toBeInTheDocument();
});
