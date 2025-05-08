import Map from "./Map";
import { getClusterSize } from "./SiteMarker";

import { markerFactory, siteFactory, statsFactory, userFactory } from "@/mocks/factories";
import { sitesResolvers } from "@/testing/resolvers/sites";
import { tileHandler } from "@/testing/resolvers/tiles";
import { usersResolvers } from "@/testing/resolvers/users";
import { render, renderWithMemoryRouter, screen, setupServer, userEvent, waitFor } from "@/utils/test-utils";

const stats = statsFactory.build();
const site = siteFactory.build({ name: "site-name", url: "https://example.com", stats });
const currentUser = userFactory.build({ username: "admin" });

const mockServer = setupServer(
  sitesResolvers.getSite.handler([site]),
  usersResolvers.getCurrentUser.handler(currentUser),
  tileHandler,
);

vi.mock("./styleSpecs", async () => {
  const actual = await vi.importActual("./styleSpecs");
  return { ...actual, naturalEarth: { ...actual.naturalEarth!, sources: {}, layers: [] } };
});

beforeAll(() => {
  mockServer.listen();
});
beforeEach(() => {
  localStorage.setItem("hasAcceptedOsmTos", JSON.stringify({ [currentUser.username]: false }));
});
afterEach(() => {
  mockServer.resetHandlers();
  localStorage.clear();
});
afterAll(() => {
  mockServer.close();
});

it("renders the map with controls", async () => {
  render(<Map markers={null} />);

  await waitFor(() => {
    expect(screen.getByRole("button", { name: /Zoom in/ })).toBeInTheDocument();
  });

  expect(screen.getByRole("button", { name: /Zoom out/ })).toBeInTheDocument();
});

it("displays open street map attribution", async () => {
  localStorage.setItem("hasAcceptedOsmTos", JSON.stringify({ admin: true }));
  const { unmount } = render(<Map markers={null} />);

  await waitFor(() => {
    expect(
      screen.getByRole("link", {
        name: /openstreetmap/i,
      }),
    ).toBeInTheDocument();
  });

  expect(
    screen.getByRole("link", {
      name: /openstreetmap/i,
    }),
  ).toHaveAttribute("href", "https://www.openstreetmap.org/copyright");

  localStorage.setItem("hasAcceptedOsmTos", JSON.stringify({ admin: false }));

  await unmount();

  render(<Map markers={null} />);
  expect(
    screen.queryByRole("link", {
      name: /openstreetmap/i,
    }),
  ).not.toBeInTheDocument();
});

it("updates markers correctly when the markers prop changes", async () => {
  const markers = markerFactory.buildList(2, { position: [0, 0] });
  const { rerender } = render(<Map markers={markers} />);

  await waitFor(() =>
    expect(screen.getByRole("button", { name: `${markers.length} sites cluster` })).toBeInTheDocument(),
  );

  const newMarkers = markerFactory.buildList(3, { position: [0, 0] });
  rerender(<Map markers={newMarkers} />);

  await waitFor(() =>
    expect(screen.getByRole("button", { name: `${newMarkers.length} sites cluster` })).toBeInTheDocument(),
  );
});

it("displays site details after clicking a marker", async () => {
  const markers = [{ ...markerFactory.build({ id: site.id, position: [0, 0] }) }];
  renderWithMemoryRouter(<Map markers={markers} />, { withMainLayout: true });
  await waitFor(() => expect(screen.getByLabelText(/site location marker/)).toBeInTheDocument());
  const marker = screen.getByRole("button", { name: /site location marker/ });
  expect(screen.queryByLabelText("Site details")).not.toBeInTheDocument();
  await userEvent.click(marker);
  expect(screen.getByLabelText("Site details")).toBeInTheDocument();
});

it("updates highestClusterChildCount correctly when more markers are added", async () => {
  const markers = markerFactory.buildList(2, { position: [0, 0] });
  const { rerender } = render(<Map markers={markers} />);

  await waitFor(() =>
    expect(screen.getByRole("button", { name: `${markers.length} sites cluster` })).toBeInTheDocument(),
  );

  const newMarkers = markerFactory.buildList(3, { position: [0, 0] });
  rerender(<Map markers={newMarkers} />);

  await waitFor(() =>
    expect(screen.queryByRole("button", { name: `${markers.length} sites cluster` })).not.toBeInTheDocument(),
  );
  await waitFor(() =>
    expect(screen.getByRole("button", { name: `${newMarkers.length} sites cluster` })).toBeInTheDocument(),
  );
});

it("sets cluster size relative to the biggest cluster currently in view", async () => {
  const count = 5;
  const markers = [...markerFactory.buildList(count, { position: [0, 0] })];
  render(<Map markers={markers} />);

  await waitFor(() => expect(screen.getByRole("button", { name: /sites cluster/ })).toBeInTheDocument());
  expect(screen.getByRole("button", { name: `${count} sites cluster` }).parentElement).toHaveStyle({
    width: `${getClusterSize(count, count)}px`,
    height: `${getClusterSize(count, count)}px`,
  });
});
