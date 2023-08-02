/* eslint-disable testing-library/no-container */
import Map from "./Map";

import { siteFactory } from "@/mocks/factories";
import { formatSiteMarker } from "@/utils";
import { render, screen, within } from "@/utils/test-utils";

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
  const { container } = render(<Map id="map-container" markers={markers} />);

  expect(container.querySelectorAll(".leaflet-marker-icon")).toHaveLength(sites.length);
  expect(within(container.querySelector(".leaflet-marker-pane")!).getAllByRole("button")).toHaveLength(sites.length);
  // TODO: ensure that each marker has an accessible label
  // markers.forEach(({ name }) => {
  //   expect(screen.getByRole("button", { name })).toBeInTheDocument();
  // });
});
