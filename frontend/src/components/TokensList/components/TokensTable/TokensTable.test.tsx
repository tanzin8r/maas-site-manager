import TokensTable from "./TokensTable";

import type { Token } from "@/api/types";
import { tokenFactory } from "@/mocks/factories";
import { render, screen, within } from "@/test-utils";

it("displays the tokens table", () => {
  render(<TokensTable data={{ items: [], total: 0, page: 1, size: 0 }} isFetchedAfterMount={true} isLoading={false} />);

  expect(screen.getByRole("table", { name: /tokens/i })).toBeInTheDocument();
});

it("displays rows for each token", () => {
  const items = tokenFactory.buildList(1);
  render(<TokensTable data={{ items, total: 0, page: 1, size: 0 }} isFetchedAfterMount={true} isLoading={false} />);

  const tableBody = screen.getAllByRole("rowgroup")[1];
  expect(within(tableBody).getAllByRole("row")).toHaveLength(items.length);
  within(tableBody)
    .getAllByRole("row")
    .forEach((row, idx) => expect(row).toHaveTextContent(new RegExp(items[idx].token, "i")));
});

it("displays a copy button in each row", () => {
  const items = tokenFactory.buildList(1);
  render(<TokensTable data={{ items, total: 0, page: 1, size: 0 }} isFetchedAfterMount={true} isLoading={false} />);

  const tableBody = screen.getAllByRole("rowgroup")[1];
  within(tableBody)
    .getAllByRole("button", { name: /copy/i })
    .forEach((btn) => {
      expect(btn).toBeInTheDocument();
    });
});

it("should display a no-tokens caption if there are no tokens", () => {
  const items: Token[] = [];
  render(<TokensTable data={{ items, total: 0, page: 1, size: 0 }} isFetchedAfterMount={true} isLoading={false} />);

  expect(screen.getByText(/No tokens available/i)).toBeInTheDocument();
});
