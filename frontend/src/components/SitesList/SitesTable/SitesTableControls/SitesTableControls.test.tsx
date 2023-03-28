import SitesTableControls from "./SitesTableControls";

import { render, screen } from "@/test-utils";

it("displays correct total number of sites", () => {
  render(
    <SitesTableControls
      allColumns={[]}
      data={{ items: [], total: 3, page: 1, size: 0 }}
      isLoading={false}
      setSearchText={() => {}}
    />,
  );

  expect(screen.getByRole("heading", { name: /3 MAAS region/i })).toBeInTheDocument();
});

it("displays a search input", () => {
  render(
    <SitesTableControls
      allColumns={[]}
      data={{ items: [], total: 1, page: 1, size: 0 }}
      isLoading={false}
      setSearchText={() => {}}
    />,
  );
  expect(
    screen.getByRole("searchbox", {
      name: /search and filter/i,
    }),
  ).toBeInTheDocument();
});
