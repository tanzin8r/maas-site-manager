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
const paginationProps = {
  currentPage: 1,
  dataContext: "MAAS Regions",
  handlePageSizeChange: vi.fn,
  isLoading: false,
  itemsPerPage: 1,
  onNextClick: vi.fn,
  onPreviousClick: vi.fn,
  setCurrentPage: vi.fn,
  totalItems: 1,
};
const commonProps = {
  error: undefined,
  isLoading: false,
  sorting: [],
  setSorting: vi.fn(),
  paginationProps: {
    ...paginationProps,
  },
  setSearchText: vi.fn(),
};

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
      {...commonProps}
      data={sitesQueryResultFactory.build()}
      paginationProps={{
        ...paginationProps,
        totalItems: 0,
      }}
    />,
  );

  expect(screen.getByRole("table", { name: /sites/i })).toBeInTheDocument();
});

it("displays rows with details for each site", () => {
  const items = siteFactory.buildList(1);
  renderWithMemoryRouter(
    <SitesTable
      {...commonProps}
      data={sitesQueryResultFactory.build({ items, total: 1, page: 1, size: 1 })}
      paginationProps={{
        ...paginationProps,
      }}
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
      {...commonProps}
      data={sitesQueryResultFactory.build({ items, total: 100, page: 1, size: pageLength })}
      error={undefined}
      isLoading={false}
      paginationProps={{
        ...paginationProps,
        itemsPerPage: pageLength,
        totalItems: 100,
      }}
      setSearchText={vi.fn()}
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
      {...commonProps}
      data={sitesQueryResultFactory.build({ items: [item], total: 1, page: 1, size: 1 })}
      error={undefined}
      isLoading={false}
      paginationProps={{
        ...paginationProps,
      }}
      setSearchText={vi.fn()}
    />,
  );

  expect(screen.getByRole("table", { name: /sites/i })).toBeInTheDocument();
  expect(screen.getByText(/13:00 UTC\+1/i)).toBeInTheDocument();
});

it("displays full name of the country", () => {
  const item = siteFactory.build({ country: "GB" });
  renderWithMemoryRouter(
    <SitesTable
      {...commonProps}
      data={sitesQueryResultFactory.build({ items: [item], total: 1, page: 1, size: 1 })}
      error={undefined}
      isLoading={false}
      paginationProps={{
        ...paginationProps,
      }}
      setSearchText={vi.fn()}
    />,
  );

  expect(screen.getByText("United Kingdom")).toBeInTheDocument();
});

it("displays correct number of deployed machines", () => {
  const item = siteFactory.build({
    stats: statsFactory.build({
      total_machines: 1000,
      deployed_machines: 100,
      allocated_machines: 200,
      ready_machines: 300,
      error_machines: 400,
    }),
  });
  renderWithMemoryRouter(
    <SitesTable
      {...commonProps}
      data={sitesQueryResultFactory.build({ items: [item], total: 1, page: 1, size: 1 })}
      paginationProps={{
        ...paginationProps,
      }}
    />,
  );

  expect(screen.getByText("100 of 1000 deployed")).toBeInTheDocument();
});

it("if name is not unique a warning is displayed.", async () => {
  const itemUnique = siteFactory.build({
    name_unique: true,
  });
  const { rerender } = renderWithMemoryRouter(
    <SitesTable
      {...commonProps}
      data={sitesQueryResultFactory.build({ items: [itemUnique], total: 1, page: 1, size: 1 })}
      paginationProps={{
        ...paginationProps,
      }}
    />,
  );

  expect(screen.queryByRole("button", { name: /warning - name is not unique/i })).not.toBeInTheDocument();

  const itemNonUnique = siteFactory.build({
    name_unique: false,
  });
  rerender(
    <SitesTable
      {...commonProps}
      data={sitesQueryResultFactory.build({ items: [itemNonUnique], total: 1, page: 1, size: 1 })}
      paginationProps={{
        ...paginationProps,
      }}
    />,
  );

  expect(screen.getByRole("button", { name: /warning - name is not unique/i })).toBeInTheDocument();
});

it("displays a pagination bar with the table", () => {
  const items = siteFactory.buildList(2);
  renderWithMemoryRouter(
    <SitesTable
      {...commonProps}
      data={sitesQueryResultFactory.build({ items, total: 2, page: 1, size: 10 })}
      paginationProps={{
        ...paginationProps,
        itemsPerPage: 10,
        totalItems: 2,
      }}
    />,
  );

  expect(screen.getByText(/Showing 2 out of 2 MAAS Regions/i)).toBeInTheDocument();
  expect(screen.getByRole("button", { name: /next page/i })).toBeInTheDocument();
  expect(screen.getByRole("button", { name: /previous page/i })).toBeInTheDocument();
});

it("displays sort direction label", async () => {
  const items = siteFactory.buildList(2);
  const { rerender } = renderWithMemoryRouter(
    <SitesTable {...commonProps} data={sitesQueryResultFactory.build({ items, total: 2, page: 1, size: 10 })} />,
  );
  const nameDescending = ["columnheader", { name: /Name descending/i }] as const;
  const nameAscending = ["columnheader", { name: /Name ascending/i }] as const;

  expect(screen.getByRole("columnheader", { name: /Name/i })).toBeInTheDocument();
  expect(screen.queryByRole(...nameDescending)).not.toBeInTheDocument();
  expect(screen.queryByRole(...nameAscending)).not.toBeInTheDocument();

  rerender(
    <SitesTable
      {...commonProps}
      data={sitesQueryResultFactory.build({ items, total: 2, page: 1, size: 10 })}
      sorting={[{ id: "name", desc: true }]}
    />,
  );

  expect(screen.getByRole(...nameDescending)).toBeInTheDocument();

  rerender(
    <SitesTable
      {...commonProps}
      data={sitesQueryResultFactory.build({ items, total: 2, page: 1, size: 10 })}
      sorting={[{ id: "name", desc: false }]}
    />,
  );

  expect(screen.getByRole(...nameAscending)).toBeInTheDocument();
});
