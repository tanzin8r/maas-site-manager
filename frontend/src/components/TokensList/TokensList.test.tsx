import { waitFor } from "@testing-library/react";

import TokensList from "./TokensList";

import urls from "@/api/urls";
import { tokenFactory } from "@/mocks/factories";
import { createMockGetTokensResolver } from "@/mocks/resolvers";
import { createMockGetServer } from "@/mocks/server";
import { screen, renderWithMemoryRouter, within } from "@/test-utils";

const tokens = tokenFactory.buildList(2);
const mockServer = createMockGetServer(urls.tokens, createMockGetTokensResolver(tokens));

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

it("should display a token count description (default=50)", () => {
  renderWithMemoryRouter(<TokensList />);

  expect(screen.getByText(new RegExp(`showing 2 out of 2 tokens`, "i"))).toBeInTheDocument();
});
