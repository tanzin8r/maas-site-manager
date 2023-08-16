import { rest } from "msw";

import Map from "./Map";

import { markerFactory, siteFactory, statsFactory } from "@/mocks/factories";
import { createMockSiteResolver } from "@/mocks/resolvers";
import { formatSiteMarker } from "@/utils";
import { apiUrls } from "@/utils/test-urls";
import { render, renderWithMemoryRouter, screen, setupServer, userEvent } from "@/utils/test-utils";

const stats = statsFactory.build();
const site = siteFactory.build({ name: "site-name", url: "https://example.com", stats });
const mockServer = setupServer(rest.get(`${apiUrls.sites}/:id`, createMockSiteResolver([site])));

beforeAll(() => {
  mockServer.listen();
});
afterEach(() => {
  mockServer.resetHandlers();
});
afterAll(() => {
  mockServer.close();
});

it("renders the map with controls", async () => {
  render(<Map id="map-container" markers={null} />);
  // expect tile images tags to use openstreetmap as the source
  expect(screen.getAllByRole("img").length).toBeGreaterThan(0);
  await screen.getAllByRole("img").forEach(async (img) => {
    await expect(img).toHaveAttribute("src", expect.stringContaining("tile.openstreetmap.org"));
  });
  expect(screen.getByRole("button", { name: /Zoom in/ })).toBeInTheDocument();
  expect(screen.getByRole("button", { name: /Zoom out/ })).toBeInTheDocument();
});

it("displays open street map attribution", () => {
  render(<Map id="map-container" markers={null} />);

  expect(
    screen.getByRole("link", {
      name: /openstreetmap/i,
    }),
  ).toBeInTheDocument();
  expect(
    screen.getByRole("link", {
      name: /openstreetmap/i,
    }),
  ).toHaveAttribute("href", "https://www.openstreetmap.org/copyright");
});

it("displays map markers", () => {
  const sites = siteFactory.buildList(2);
  const markers = sites.map(formatSiteMarker);
  render(<Map id="map-container" markers={markers} />);

  const markerButtons = screen.getAllByRole("button", {
    name: /site location marker/,
  });
  expect(markerButtons).toHaveLength(sites.length);
  markerButtons.forEach((marker) => {
    expect(marker).toBeVisible();
  });
});

it("displays site details after clicking a marker", async () => {
  const markers = [{ ...markerFactory.build({ id: site.id, position: [0, 0] }) }];
  renderWithMemoryRouter(<Map id="map-container" markers={markers} />, { withMainLayout: true });
  expect(screen.getByLabelText(/site location marker/)).toBeInTheDocument();
  const marker = screen.getByRole("button", { name: /site location marker/ });
  const siteDetails = /Site details/i;
  expect(screen.queryByLabelText(siteDetails)).not.toBeInTheDocument();
  await userEvent.click(marker);
  expect(screen.getByLabelText(siteDetails)).toBeInTheDocument();
});
