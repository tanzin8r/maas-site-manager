import SiteSelection from "./SiteSelection";

import { siteFactory } from "@/mocks/factories";
import { renderWithMemoryRouter, screen } from "@/utils/test-utils";

const siteDetails = { name: "test site", url: "http://example.com" };
const site = siteFactory.build(siteDetails);

it("displays the sidepanel with a selected sites table", () => {
  renderWithMemoryRouter(<SiteSelection selectedSites={[site]} />);

  expect(screen.getByRole("heading", { name: /selection/i })).toBeInTheDocument();
  expect(screen.getByRole("table", { name: /selected sites/i })).toBeInTheDocument();
});

it("displays selected site count", () => {
  renderWithMemoryRouter(<SiteSelection selectedSites={[site]} />);

  expect(screen.getByText(/1 selected/i)).toBeInTheDocument();
});

it("displays a clear selection button", () => {
  renderWithMemoryRouter(<SiteSelection selectedSites={[site]} />);

  expect(screen.getByRole("button", { name: /clear selection/i })).toBeInTheDocument();
});
