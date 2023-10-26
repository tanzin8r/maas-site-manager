import { rest } from "msw";

import Map from "./Map";
import { getClusterSize } from "./SiteMarker";

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
  render(<Map markers={null} />);
  // expect tile images tags to use openstreetmap as the source
  expect(screen.getAllByRole("img").length).toBeGreaterThan(0);
  await screen.getAllByRole("img").forEach(async (img) => {
    await expect(img).toHaveAttribute("src", expect.stringContaining("tile.openstreetmap.org"));
  });
  expect(screen.getByRole("button", { name: /Zoom in/ })).toBeInTheDocument();
  expect(screen.getByRole("button", { name: /Zoom out/ })).toBeInTheDocument();
});

it("displays open street map attribution", () => {
  render(<Map markers={null} />);

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

it("displays individual map markers", () => {
  const sites = [siteFactory.build({ coordinates: [0, 0] })];
  const markers = sites.map(formatSiteMarker);

  render(<Map markers={markers} />);
  expect(
    screen.getByRole("button", {
      name: /site location marker/,
    }),
  ).toBeVisible();
});

it("displays nearby map markers as clusters", () => {
  const sites = siteFactory.buildList(2, { coordinates: [0, 0] });
  const markers = sites.map(formatSiteMarker);

  render(<Map markers={markers} />);
  expect(
    screen.queryByRole("button", {
      name: /site location marker/,
    }),
  ).not.toBeInTheDocument();

  expect(screen.getByRole("button", { name: `${sites.length}` })).toBeInTheDocument();
});

it("updates markers correctly when the markers prop changes", () => {
  const markers = markerFactory.buildList(2, { position: [0, 0] });
  const { rerender } = render(<Map markers={markers} />);

  expect(screen.getByRole("button", { name: `${markers.length}` })).toBeInTheDocument();

  const newMarkers = markerFactory.buildList(3, { position: [0, 0] });
  rerender(<Map markers={newMarkers} />);

  expect(screen.getByRole("button", { name: `${newMarkers.length}` })).toBeInTheDocument();
});

it("displays site details after clicking a marker", async () => {
  const markers = [{ ...markerFactory.build({ id: site.id, position: [0, 0] }) }];
  renderWithMemoryRouter(<Map markers={markers} />, { withMainLayout: true });
  expect(screen.getByLabelText(/site location marker/)).toBeInTheDocument();
  const marker = screen.getByRole("button", { name: /site location marker/ });
  expect(screen.queryByLabelText("Site details")).not.toBeInTheDocument();
  await userEvent.click(marker);
  expect(screen.getByLabelText("Site details")).toBeInTheDocument();
});

it("updates highestClusterChildCount correctly when more markers are added", () => {
  const markers = markerFactory.buildList(2, { position: [0, 0] });
  const { rerender } = render(<Map markers={markers} />);

  expect(screen.getByRole("button", { name: `${markers.length}` })).toBeInTheDocument();

  const newMarkers = markerFactory.buildList(3, { position: [0, 0] });
  rerender(<Map markers={newMarkers} />);

  expect(screen.queryByRole("button", { name: `${markers.length}` })).not.toBeInTheDocument();
  expect(screen.getByRole("button", { name: `${newMarkers.length}` })).toBeInTheDocument();
});

it("sets cluster size relative to the biggest cluster currently in view", () => {
  const count = 5;
  const markers = [...markerFactory.buildList(count, { position: [0, 0] })];
  render(<Map markers={markers} />);

  expect(screen.getByRole("button", { name: `${count}` })).toHaveStyle({
    width: `${getClusterSize(count, count)}px`,
    height: `${getClusterSize(count, count)}px`,
  });
});
