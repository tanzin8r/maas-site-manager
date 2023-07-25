import { rest } from "msw";

import RegionSummary from "./RegionSummary";

import urls from "@/api/urls";
import { siteFactory, statsFactory } from "@/mocks/factories";
import { createMockSiteResolver } from "@/mocks/resolvers";
import { renderWithMemoryRouter, waitFor, screen, setupServer, userEvent } from "@/utils/test-utils";

const stats = statsFactory.build();
const site = siteFactory.build({ url: "https://example.com", stats });
const mockServer = setupServer(rest.get(`${urls.sites}/:id`, createMockSiteResolver([site])));

beforeAll(() => {
  mockServer.listen();
});

afterEach(() => {
  mockServer.resetHandlers();
});

afterAll(() => {
  mockServer.close();
});

it("displays data for a site", async () => {
  renderWithMemoryRouter(<RegionSummary id={site.id} />);

  await waitFor(() => {
    expect(screen.getByText(site.name)).toBeInTheDocument();
  });

  expect(screen.getByRole("link", { name: site.url })).toBeInTheDocument();
  expect(screen.getByText(new RegExp(site.connection_status, "i"))).toBeInTheDocument();
  expect(screen.getByText(stats.total_machines)).toBeInTheDocument();

  await userEvent.click(screen.getByTestId("popover-container"));

  expect(screen.getByTestId("deployed")).toHaveTextContent(stats.deployed_machines.toString());
  expect(screen.getByTestId("allocated")).toHaveTextContent(stats.allocated_machines.toString());
  expect(screen.getByTestId("ready")).toHaveTextContent(stats.ready_machines.toString());
  expect(screen.getByTestId("error")).toHaveTextContent(stats.error_machines.toString());
});
