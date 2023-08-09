import SitesTableControls from "./SitesTableControls";

import { renderWithMemoryRouter, screen } from "@/utils/test-utils";

it("displays correct total number of sites", () => {
  renderWithMemoryRouter(<SitesTableControls isLoading={false} setSearchText={() => {}} totalSites={3} />);

  expect(screen.getByRole("heading", { name: /3 MAAS region/i })).toBeInTheDocument();
});

it("displays a search input", () => {
  renderWithMemoryRouter(<SitesTableControls isLoading={false} setSearchText={() => {}} totalSites={1} />);
  expect(
    screen.getByRole("searchbox", {
      name: /search and filter/i,
    }),
  ).toBeInTheDocument();
});

it("displays the sites view control tabs", () => {
  renderWithMemoryRouter(<SitesTableControls isLoading={false} setSearchText={() => {}} totalSites={1} />);

  expect(
    screen.getByRole("tablist", {
      name: /sites view control/i,
    }),
  ).toBeInTheDocument();
});
