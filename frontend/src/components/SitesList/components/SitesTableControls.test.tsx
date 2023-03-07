import { render, screen } from "../../../test-utils";

import SitesTableControls from "./SitesTableControls";

it("displays correct total number of sites", () => {
  render(<SitesTableControls allColumns={[]} data={{ items: [], total: 3, page: 1, size: 0 }} isLoading={false} />);

  expect(screen.getByRole("heading", { name: /3 MAAS region/i })).toBeInTheDocument();
});
