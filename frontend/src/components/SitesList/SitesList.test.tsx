import urls from "../../api/urls";
import { sites } from "../../mocks/factories";
import { createMockGetServer } from "../../mocks/server";
import { render, screen, waitFor, within } from "../../test-utils";

import SitesList from "./SitesList";

const sitesData = sites();
const mockServer = createMockGetServer(urls.sites, sitesData);

beforeAll(() => {
  mockServer.listen();
});
afterEach(() => {
  mockServer.resetHandlers();
});
afterAll(() => {
  mockServer.close();
});

it("renders header", () => {
  render(<SitesList />);

  expect(screen.getByRole("heading", { name: /MAAS Regions/i })).toBeInTheDocument();
});

it("displays loading text", () => {
  render(<SitesList />);

  expect(screen.getByText(/loading/i)).toBeInTheDocument();
});

it("displays populated sites table", async () => {
  const { items } = sitesData;
  render(<SitesList />);

  await waitFor(() => expect(screen.getByRole("table", { name: /sites/i })).toBeInTheDocument());

  expect(screen.getAllByRole("rowgroup")).toHaveLength(2);
  expect(screen.getByRole("heading", { name: /2 MAAS Regions/i })).toBeInTheDocument();
  const tableBody = screen.getAllByRole("rowgroup")[1];
  expect(within(tableBody).getAllByRole("row")).toHaveLength(items.length);
  within(tableBody)
    .getAllByRole("row")
    .forEach((row, i) => expect(row).toHaveTextContent(new RegExp(items[i].name, "i")));
});
