import { setupServer } from "msw/node";

import SyncStatus from "./SyncStatus";

import { siteFactory, imageFactory } from "@/mocks/factories";
import { sitesResolvers } from "@/testing/resolvers/sites";
import { renderWithMemoryRouter, screen, waitFor } from "@/utils/test-utils";

const sites = siteFactory.buildList(5);
const mockServer = setupServer(sitesResolvers.listSites.handler(sites));

beforeAll(() => {
  mockServer.listen();
});

afterEach(() => {
  mockServer.resetHandlers();
  localStorage.clear();
});

afterAll(() => {
  mockServer.close();
});

test("displays SyncedStatus when image is synced", async () => {
  const image = imageFactory.build({
    downloaded: 100,
  });

  renderWithMemoryRouter(<SyncStatus image={image} />);
  await waitFor(() => expect(screen.getByText("Synced to MAAS sites")).toBeInTheDocument());
});

test("displays QueuedStatus when image is queued", () => {
  const image = imageFactory.build({
    downloaded: 0,
  });

  renderWithMemoryRouter(<SyncStatus image={image} />);
  expect(screen.getByText("Queued for download")).toBeInTheDocument();
});

test("displays DownloadingStatus when image is downloading", () => {
  const image = imageFactory.build({
    downloaded: 1,
  });

  renderWithMemoryRouter(<SyncStatus image={image} />);
  expect(screen.getByText("Downloading 1%")).toBeInTheDocument();
});
