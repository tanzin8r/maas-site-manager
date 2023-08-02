import type { RenderResult } from "@testing-library/react";
import { rest } from "msw";

import RegionDetails from "./RegionDetails";

import urls from "@/api/urls";
import { RegionDetailsContext } from "@/context/RegionDetailsContext";
import { siteFactory, statsFactory } from "@/mocks/factories";
import { createMockSiteResolver } from "@/mocks/resolvers";
import { getCountryName, getTimeInTimezone, getTimezoneUTCString } from "@/utils";
import { screen, renderWithMemoryRouter, setupServer, waitFor } from "@/utils/test-utils";

const stats = statsFactory.build();
const site = siteFactory.build({ stats });
const mockServer = setupServer(rest.get(`${urls.sites}/:id`, createMockSiteResolver([site])));

const renderForm = (): RenderResult => {
  return renderWithMemoryRouter(
    <RegionDetailsContext.Provider value={{ regionId: site.id, setRegionId: vi.fn() }}>
      <RegionDetails />
    </RegionDetailsContext.Provider>,
  );
};

beforeAll(() => {
  mockServer.listen();
});

afterEach(() => {
  mockServer.resetHandlers();
});

afterAll(() => {
  mockServer.close();
});

it("renders the correct details for a region", async () => {
  renderForm();

  await waitFor(() => {
    expect(screen.getByRole("heading", { name: site.name })).toBeInTheDocument();
  });
  expect(screen.getByRole("link", { name: site.url })).toHaveAttribute("href", site.url);

  expect(screen.getByText(new RegExp(site.connection_status, "i"))).toBeInTheDocument();
  expect(screen.getByText(getCountryName(site.country))).toBeInTheDocument();
  expect(screen.getByText(site.street)).toBeInTheDocument();
  expect(screen.getByText(site.zip)).toBeInTheDocument();
  expect(
    screen.getByText(`${getTimeInTimezone(new Date(), site.timezone)} UTC${getTimezoneUTCString(site.timezone)}`),
  ).toBeInTheDocument();
  expect(screen.getByText(stats.total_machines)).toBeInTheDocument();

  expect(screen.getByTestId("deployed-machines")).toHaveTextContent(stats.deployed_machines.toString());
  expect(screen.getByTestId("allocated-machines")).toHaveTextContent(stats.allocated_machines.toString());
  expect(screen.getByTestId("ready-machines")).toHaveTextContent(stats.ready_machines.toString());
  expect(screen.getByTestId("error-machines")).toHaveTextContent(stats.error_machines.toString());
});
