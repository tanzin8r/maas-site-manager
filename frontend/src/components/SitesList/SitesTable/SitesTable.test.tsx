import * as timezoneMock from "timezone-mock";
import { vi } from "vitest";

import SitesTable from "./SitesTable";

import urls from "@/api/urls";
import { enrollmentRequestFactory, siteFactory, sitesQueryResultFactory } from "@/mocks/factories";
import { createMockGetEnrollmentRequestsResolver } from "@/mocks/resolvers";
import { createMockGetServer } from "@/mocks/server";
import { render, renderWithMemoryRouter, screen, within } from "@/test-utils";

const enrollmentRequests = enrollmentRequestFactory.buildList(2);
const mockServer = createMockGetServer(
  urls.enrollmentRequests,
  createMockGetEnrollmentRequestsResolver(enrollmentRequests),
);

beforeEach(() => {
  vi.useFakeTimers();
  timezoneMock.register("Etc/GMT");
  mockServer.listen();
});

afterEach(() => {
  timezoneMock.unregister();
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
  render(
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
  render(
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
  const date = new Date("2000-01-01T12:00:00Z");
  vi.setSystemTime(date);

  const item = siteFactory.build({ timezone: 1 });
  render(
    <SitesTable
      data={sitesQueryResultFactory.build({ items: [item], total: 1, page: 1, size: 1 })}
      isFetchedAfterMount={true}
      isLoading={false}
      setSearchText={() => {}}
    />,
  );

  expect(screen.getByRole("table", { name: /sites/i })).toBeInTheDocument();
  expect(screen.getByText(/13:00 UTC\+01:00/i)).toBeInTheDocument();
});

it("displays full name of the country", () => {
  const item = siteFactory.build({ address: { countrycode: "GB" } });
  render(
    <SitesTable
      data={sitesQueryResultFactory.build({ items: [item], total: 1, page: 1, size: 1 })}
      isFetchedAfterMount={true}
      isLoading={false}
      setSearchText={() => {}}
    />,
  );

  expect(screen.getByText("United Kingdom")).toBeInTheDocument();
});
