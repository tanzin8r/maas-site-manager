import SitesTable from "./SitesTable";

import urls from "@/api/urls";
import { enrollmentRequestFactory, siteFactory, sitesQueryResultFactory, statsFactory } from "@/mocks/factories";
import { createMockGetEnrollmentRequestsResolver } from "@/mocks/resolvers";
import { createMockGetServer } from "@/mocks/server";
import { renderWithMemoryRouter, screen, within } from "@/test-utils";

const enrollmentRequests = enrollmentRequestFactory.buildList(2);
const mockServer = createMockGetServer(
  urls.enrollmentRequests,
  createMockGetEnrollmentRequestsResolver(enrollmentRequests),
);

beforeEach(() => {
  vi.useFakeTimers();
  mockServer.listen();
});

afterEach(() => {
  vi.useRealTimers();
  mockServer.resetHandlers();
});

afterAll(() => {
  mockServer.close();
});

it("displays an empty sites table", () => {
  renderWithMemoryRouter(
    <SitesTable
      data={sitesQueryResultFactory.build()}
      isFetchedAfterMount={true}
      isLoading={false}
      setSearchText={() => {}}
    />,
  );

  expect(screen.getByRole("table", { name: /sites/i })).toBeInTheDocument();
});

it("displays rows with details for each site", () => {
  const items = siteFactory.buildList(1);
  renderWithMemoryRouter(
    <SitesTable
      data={sitesQueryResultFactory.build({ items, total: 1, page: 1, size: 1 })}
      isFetchedAfterMount={true}
      isLoading={false}
      setSearchText={() => {}}
    />,
  );

  expect(screen.getByRole("table", { name: /sites/i })).toBeInTheDocument();

  const tableBody = screen.getAllByRole("rowgroup")[1];
  expect(within(tableBody).getAllByRole("row")).toHaveLength(items.length);
  within(tableBody)
    .getAllByRole("row")
    .forEach((row, i) => expect(row).toHaveTextContent(new RegExp(items[i].name, "i")));
});

it("displays correctly paginated results", () => {
  const pageLength = 50;
  const items = siteFactory.buildList(pageLength);
  renderWithMemoryRouter(
    <SitesTable
      data={sitesQueryResultFactory.build({ items, total: 100, page: 1, size: pageLength })}
      isFetchedAfterMount={true}
      isLoading={false}
      setSearchText={() => {}}
    />,
  );

  const tableBody = screen.getAllByRole("rowgroup")[1];
  expect(within(tableBody).getAllByRole("row")).toHaveLength(pageLength);
});

it("displays correct local time", () => {
  const date = new Date("Fri Apr 21 2023 12:00:00 GMT+0000 (GMT)");
  vi.setSystemTime(date);

  const item = siteFactory.build({ timezone: "Europe/London" });
  renderWithMemoryRouter(
    <SitesTable
      data={sitesQueryResultFactory.build({ items: [item], total: 1, page: 1, size: 1 })}
      isFetchedAfterMount={true}
      isLoading={false}
      setSearchText={() => {}}
    />,
  );

  expect(screen.getByRole("table", { name: /sites/i })).toBeInTheDocument();
  expect(screen.getByText(/13:00 UTC\+1/i)).toBeInTheDocument();
});

it("displays full name of the country", () => {
  const item = siteFactory.build({ address: { countrycode: "GB" } });
  renderWithMemoryRouter(
    <SitesTable
      data={sitesQueryResultFactory.build({ items: [item], total: 1, page: 1, size: 1 })}
      isFetchedAfterMount={true}
      isLoading={false}
      setSearchText={() => {}}
    />,
  );

  expect(screen.getByText("United Kingdom")).toBeInTheDocument();
});

it("displays correct number of deployed machines", () => {
  const item = siteFactory.build({
    stats: statsFactory.build({
      deployed_machines: 100,
      allocated_machines: 200,
      ready_machines: 300,
      error_machines: 400,
    }),
  });
  renderWithMemoryRouter(
    <SitesTable
      data={sitesQueryResultFactory.build({ items: [item], total: 1, page: 1, size: 1 })}
      isFetchedAfterMount={true}
      isLoading={false}
      setSearchText={() => {}}
    />,
  );

  expect(screen.getByText("100 of 1000 deployed")).toBeInTheDocument();
});
