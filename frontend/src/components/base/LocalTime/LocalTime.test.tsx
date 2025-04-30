import LocalTime from "./LocalTime";

import { TimeZone } from "@/apiclient";
import { siteFactory } from "@/mocks/factories";
import { render, screen } from "@/utils/test-utils";

const site = siteFactory.build({ timezone: TimeZone.EUROPE_ISLE_OF_MAN });

it("correctly shows local time for a given time zone", () => {
  const { timezone } = site;
  const date = new Date("Sat Apr 20 2069 14:00:00 GMT+0200 (GMT)");
  vi.setSystemTime(date);
  render(<LocalTime timezone={timezone!} />);
  expect(screen.getByText(/13:00 UTC\+1/i)).toBeInTheDocument();
});
