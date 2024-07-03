import SiteSelectionTable from "./SiteSelectionTable";

import { siteFactory } from "@/mocks/factories";
import { renderWithMemoryRouter, screen, userEvent, waitFor, within } from "@/utils/test-utils";

const siteDetails = { name: "test site", url: "http://example.com" };
const site = siteFactory.build(siteDetails);

it("renders the site selection table", () => {
  renderWithMemoryRouter(<SiteSelectionTable selectedSites={[site]} />);

  expect(screen.getByRole("table", { name: /selected sites/i }));
});

it("displays a list of selected sites", () => {
  renderWithMemoryRouter(<SiteSelectionTable selectedSites={[site]} />);

  const tableBody = screen.getAllByRole("rowgroup")[1];
  expect(within(tableBody).getAllByRole("row")).toHaveLength(1);
  expect(within(tableBody).getByText(siteDetails.name)).toBeInTheDocument();
  expect(within(tableBody).getByText(siteDetails.url)).toBeInTheDocument();
});

it("has an unselect button for each row", () => {
  renderWithMemoryRouter(<SiteSelectionTable selectedSites={[site]} />);

  const tableBody = screen.getAllByRole("rowgroup")[1];
  expect(within(tableBody).getByRole("button", { name: /unselect/i })).toBeInTheDocument();
});

it("unselect button has a tooltop", async () => {
  renderWithMemoryRouter(<SiteSelectionTable selectedSites={[site]} />);

  const tableBody = screen.getAllByRole("rowgroup")[1];
  await userEvent.hover(within(tableBody).getByRole("button", { name: /unselect/i }));
  await waitFor(() => {
    expect(screen.getByRole("tooltip", { name: /remove from selection/i })).toBeInTheDocument();
  });
});
