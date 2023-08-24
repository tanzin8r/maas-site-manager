import { waitFor } from "@testing-library/react";
import { rest } from "msw";
import { setupServer } from "msw/node";

import TokensList from "./TokensList";

import { tokenFactory } from "@/mocks/factories";
import { createMockDeleteTokenResolver, createMockGetTokensResolver } from "@/mocks/resolvers";
import { apiUrls } from "@/utils/test-urls";
import { screen, renderWithMemoryRouter, within, userEvent } from "@/utils/test-utils";

const tokens = tokenFactory.buildList(2);
const handlers = [
  rest.get(apiUrls.tokens, createMockGetTokensResolver(tokens)),
  rest.delete(`${apiUrls.tokens}/:id`, createMockDeleteTokenResolver()),
];
const mockServer = setupServer(...handlers);

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
    .forEach((row, idx) => expect(row).toHaveTextContent(new RegExp(tokens[idx].value, "i")));
});

it("should display a token count description", async () => {
  renderWithMemoryRouter(<TokensList />);

  // Wait for data to load
  await waitFor(() => {
    expect(screen.queryByText(/Loading/i)).not.toBeInTheDocument();
  });

  expect(screen.getByText(new RegExp(`showing 2 out of 2 tokens`, "i"))).toBeInTheDocument();
});

it("disables the Delete button if no rows are selected", async () => {
  renderWithMemoryRouter(<TokensList />);

  expect(screen.getByRole("button", { name: "Delete" })).toBeDisabled();

  await userEvent.click(screen.getAllByRole("checkbox")[0]);

  expect(screen.getByRole("button", { name: "Delete" })).toBeEnabled();
});

it("Export button is enabled regardless of row selection", async () => {
  renderWithMemoryRouter(<TokensList />);

  expect(screen.getByRole("button", { name: "Export" })).toBeEnabled();

  await userEvent.click(screen.getAllByRole("checkbox")[0]);

  expect(screen.getByRole("button", { name: "Export" })).toBeEnabled();
});

it("displays a notification after a successful single deletion", async () => {
  renderWithMemoryRouter(<TokensList />);

  // Wait for data to load
  await waitFor(() => {
    expect(screen.queryByText(/Loading/i)).not.toBeInTheDocument();
  });

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

  // Wait for data to load
  await waitFor(() => {
    expect(screen.queryByText(/Loading/i)).not.toBeInTheDocument();
  });

  const checkboxes = screen.getAllByRole("checkbox");
  await userEvent.click(checkboxes[1]);
  await userEvent.click(checkboxes[2]);
  await userEvent.click(screen.getByRole("button", { name: /delete/i }));

  await waitFor(() => {
    expect(screen.getByText(/2 enrollment tokens were deleted\./i)).toBeInTheDocument();
  });
});

// TODO: enable once implemented https://warthogs.atlassian.net/browse/MAASENG-2066
it.skip("displays an error notification after failed deletion", async () => {
  mockServer.resetHandlers(
    rest.get(apiUrls.tokens, createMockGetTokensResolver(tokens)),
    rest.delete(apiUrls.tokens, (_req, res, ctx) => res(ctx.status(400, "BAD REQUEST"))),
  );
  renderWithMemoryRouter(<TokensList />);

  // Wait for data to load
  await waitFor(() => {
    expect(screen.queryByText(/Loading/i)).not.toBeInTheDocument();
  });

  await userEvent.click(screen.getAllByRole("checkbox")[1]);
  await userEvent.click(screen.getByRole("button", { name: /delete/i }));

  await waitFor(() => {
    expect(
      screen.getByRole("heading", {
        name: /error/i,
      }),
    ).toBeInTheDocument();
  });
});
