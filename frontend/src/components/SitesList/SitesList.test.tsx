import SitesList from "./SitesList";
import { render, screen } from "../../test-utils";

it("renders header", () => {
  render(<SitesList />);

  expect(
    screen.getByRole("heading", { name: /MAAS Regions/i })
  ).toBeInTheDocument();
});
