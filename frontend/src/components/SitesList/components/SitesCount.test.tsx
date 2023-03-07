import { siteFactory } from "../../../mocks/factories";
import { render, screen } from "../../../test-utils";

import SitesCount from "./SitesCount";

it("displays plural sites count", () => {
  const total = 11;
  const items = siteFactory.buildList(total);
  render(<SitesCount data={{ items, total, page: 1, size: 1 }} isLoading={false} />);

  expect(screen.getByText("11 MAAS regions")).toBeInTheDocument();
});

it("displays singular sites count", () => {
  const total = 1;
  const items = siteFactory.buildList(total);
  render(<SitesCount data={{ items, total, page: 1, size: 1 }} isLoading={false} />);

  expect(screen.getByText("1 MAAS region")).toBeInTheDocument();
});
