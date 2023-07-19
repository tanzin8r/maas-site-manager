import SitesList from "./SitesList";

import urls from "@/api/urls";
import { siteFactory } from "@/mocks/factories";
import { createMockSitesResolver } from "@/mocks/resolvers";
import { createMockGetServer } from "@/mocks/server";
import { renderWithMemoryRouter, screen, userEvent, waitFor, within } from "@/test-utils";

const sites = siteFactory.buildList(2);
const mockServer = createMockGetServer(urls.sites, createMockSitesResolver(sites));

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

it("displays loading text", () => {
  renderWithMemoryRouter(<SitesList />);

  expect(within(screen.getByRole("table", { name: /sites/i })).getByText(/loading/i)).toBeInTheDocument();
});

it("displays populated sites table", async () => {
  renderWithMemoryRouter(<SitesList />);

  expect(screen.getByRole("table", { name: /sites/i })).toBeInTheDocument();

  await waitFor(() => expect(screen.getAllByRole("rowgroup")).toHaveLength(2));
  const tableBody = screen.getAllByRole("rowgroup")[1];
  expect(within(tableBody).getAllByRole("row")).toHaveLength(sites.length);
  within(tableBody)
    .getAllByRole("row")
    .forEach((row, i) => expect(row).toHaveTextContent(new RegExp(sites[i].name, "i")));
});

it("disables the 'remove' button if no rows are selected", async () => {
  renderWithMemoryRouter(<SitesList />);
  await expect(screen.getByRole("button", { name: /Remove/i })).toBeDisabled();
});

it("enables the 'remove' button if some rows are selected", async () => {
  renderWithMemoryRouter(<SitesList />);
  await userEvent.click(screen.getByRole("checkbox", { name: /select all/i }));
  await waitFor(() => expect(screen.getByRole("button", { name: /Remove/i })).toBeEnabled());
});

it("can hide and unhide columns", async () => {
  renderWithMemoryRouter(<SitesList />);
  expect(screen.getByRole("columnheader", { name: /Connection/i })).toBeInTheDocument();

  await userEvent.click(screen.getByRole("button", { name: "Columns" }));

  [/Connection/i, /Address/i, /Time/i, /Machines/i, /Status/i].forEach((name) => {
    expect(screen.getByRole("checkbox", { name })).toBeInTheDocument();
  });

  await userEvent.click(screen.getByRole("checkbox", { name: /Connection/i }));

  expect(screen.getByRole("checkbox", { name: "4 out of 5 selected" })).toBeInTheDocument();
  expect(screen.queryByRole("columnheader", { name: /Connection/i })).not.toBeInTheDocument();

  await userEvent.click(screen.getByRole("checkbox", { name: /Connection/i }));

  expect(screen.getByRole("checkbox", { name: "5 out of 5 selected" })).toBeInTheDocument();
  expect(screen.getByRole("columnheader", { name: /Connection/i })).toBeInTheDocument();
});

it("can hide and unhide all columns", async () => {
  renderWithMemoryRouter(<SitesList />);

  expect(screen.getByRole("columnheader", { name: /Connection/i })).toBeInTheDocument();
  expect(screen.getByRole("columnheader", { name: /Country/i })).toBeInTheDocument();
  expect(screen.getByRole("columnheader", { name: /Local time/i })).toBeInTheDocument();
  expect(screen.getByRole("columnheader", { name: /Machines/i })).toBeInTheDocument();

  await userEvent.click(screen.getByRole("button", { name: "Columns" }));
  await userEvent.click(screen.getByRole("checkbox", { name: "5 out of 5 selected" }));

  expect(screen.getByRole("checkbox", { name: "0 out of 5 selected" })).toBeInTheDocument();

  expect(screen.queryByRole("columnheader", { name: /Connection/i })).not.toBeInTheDocument();
  expect(screen.queryByRole("columnheader", { name: /Country/i })).not.toBeInTheDocument();
  expect(screen.queryByRole("columnheader", { name: /Local time/i })).not.toBeInTheDocument();
  expect(screen.queryByRole("columnheader", { name: /Machines/i })).not.toBeInTheDocument();

  await userEvent.click(screen.getByRole("checkbox", { name: "0 out of 5 selected" }));

  expect(screen.getByRole("columnheader", { name: /Connection/i })).toBeInTheDocument();
  expect(screen.getByRole("columnheader", { name: /Country/i })).toBeInTheDocument();
  expect(screen.getByRole("columnheader", { name: /Local time/i })).toBeInTheDocument();
  expect(screen.getByRole("columnheader", { name: /Machines/i })).toBeInTheDocument();
});

it("toggles select all checkbox on click", async () => {
  renderWithMemoryRouter(<SitesList />);

  const checkbox = screen.getByRole("checkbox", { name: /select all/i });
  await expect(checkbox).not.toBeChecked();

  await userEvent.click(checkbox);

  await expect(checkbox).toBeChecked();
});
