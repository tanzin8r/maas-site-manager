import { render, screen } from "../../test-utils";

import SitesList from "./SitesList";

it("renders header", () => {
  render(<SitesList />);

  expect(screen.getByRole("heading", { name: /MAAS Regions/i })).toBeInTheDocument();
});
