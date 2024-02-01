import { rest } from "msw";
import { setupServer } from "msw/node";

import SyncStatus from "./SyncStatus";

import { siteFactory, imageFactory } from "@/mocks/factories";
import { createMockSitesResolver } from "@/mocks/resolvers";
import { createMockGetServer } from "@/mocks/server";
import { apiUrls } from "@/utils/test-urls";
import { renderWithMemoryRouter, screen, waitFor } from "@/utils/test-utils";

const sites = siteFactory.buildList(5);
const mockServer = createMockGetServer(apiUrls.sites, createMockSitesResolver(sites));

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
const server = setupServer(
  rest.get("/api/sites", (req, res, ctx) => {
    return res(ctx.json({ total: 5 }));
  }),
);

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

test("displays SyncedStatus when image is synced", async () => {
  const lastSynced = new Date("2023-04-21T11:30:00.000Z").toISOString();
  const image = imageFactory.build({
    downloaded: 100,
    number_of_sites_synced: 5,
    last_synced: lastSynced,
  });

  renderWithMemoryRouter(<SyncStatus image={image} />);
  await waitFor(() => expect(screen.getByText("Synced to MAAS sites")).toBeInTheDocument());
  expect(screen.getByText(/2023-04-21 11:30/)).toBeInTheDocument();
});

test("displays SyncingStatus when image is syncing", async () => {
  const image = imageFactory.build({
    downloaded: 1,
    number_of_sites_synced: 3,
    last_synced: null,
  });

  renderWithMemoryRouter(<SyncStatus image={image} />);
  expect(screen.getByText("Syncing to MAAS sites")).toBeInTheDocument();
  await waitFor(() => expect(screen.getByText("3 / 5")).toBeInTheDocument());
});

test("displays QueuedStatus when image is queued", () => {
  const image = imageFactory.build({
    downloaded: 0,
    number_of_sites_synced: 0,
    last_synced: null,
  });

  renderWithMemoryRouter(<SyncStatus image={image} />);
  expect(screen.getByText("Queued for download")).toBeInTheDocument();
});

test("displays DownloadingStatus when image is downloading", () => {
  const image = imageFactory.build({
    downloaded: 1,
    number_of_sites_synced: 0,
    last_synced: null,
  });

  renderWithMemoryRouter(<SyncStatus image={image} />);
  expect(screen.getByText("Downloading 1%")).toBeInTheDocument();
});

test("displays SyncingStatus with unknown total sites when totalSites is null", () => {
  const image = imageFactory.build({
    downloaded: 1,
    number_of_sites_synced: 3,
    last_synced: null,
  });

  mockServer.resetHandlers(
    rest.get(apiUrls.sites, (req, res, ctx) => {
      return res(ctx.delay(Infinity));
    }),
  );

  renderWithMemoryRouter(<SyncStatus image={image} />);
  expect(screen.getByText("Syncing to MAAS sites")).toBeInTheDocument();
  expect(screen.getByText("3 / unknown")).toBeInTheDocument();
});
