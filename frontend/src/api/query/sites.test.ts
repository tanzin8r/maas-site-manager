import { setupServer } from "msw/node";

import { useDeleteSites, useEditSite, useSite, useSites, useSitesCoordinates } from "./sites";

import type { SiteCoordinates, SiteUpdateRequest } from "@/apiclient";
import { siteFactory } from "@/mocks/factories";
import { sitesResolvers } from "@/testing/resolvers/sites";
import { renderHook, waitFor, Providers } from "@/utils/test-utils";

const sitesData = siteFactory.buildList(2);
const mockServer = setupServer(
  sitesResolvers.listSites.handler(sitesData),
  sitesResolvers.sitesCoordinates.handler(sitesData),
  sitesResolvers.getSite.handler(sitesData),
  sitesResolvers.updateSites.handler(),
  sitesResolvers.deleteSites.handler(),
);

beforeAll(() => {
  mockServer.listen();
});
afterEach(() => {
  mockServer.resetHandlers();
});
afterAll(() => {
  mockServer.close();
});

describe("useSites", () => {
  it("should return sites", async () => {
    const { result } = renderHook(() => useSites({ query: { page: 1, size: 2 } }), { wrapper: Providers });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(result.current.data!.items).toEqual(sitesData);
  });
});

describe("useSitesCoordinates", () => {
  it("should return sites coordinates", async () => {
    const { result } = renderHook(() => useSitesCoordinates(), { wrapper: Providers });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(result.current.data!).toEqual(
      sitesData.map((site): SiteCoordinates => ({ id: site.id, coordinates: site.coordinates })),
    );
  });
});

describe("useSite", () => {
  it("should return a specific site", async () => {
    const expectedSite = sitesData[0];
    const { result } = renderHook(() => useSite({ path: { id: expectedSite.id } }), {
      wrapper: Providers,
    });

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    expect(result.current.data).toEqual(expectedSite);
  });

  it("should return error if site does not exist", async () => {
    const { result } = renderHook(() => useSite({ path: { id: 999 } }), {
      wrapper: Providers,
    });

    await waitFor(() => {
      expect(result.current.isError).toBe(true);
    });
  });
});

describe("useUpdateSite", () => {
  it("should update an existing site", async () => {
    const siteToUpdate = sitesData[0];
    const updateData: SiteUpdateRequest = {
      note: "Edited",
    };

    const { result } = renderHook(() => useEditSite(), { wrapper: Providers });
    result.current.mutate({ body: updateData, path: { id: siteToUpdate.id } });

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });
  });
});

describe("useDeleteSites", () => {
  it("should delete a site", async () => {
    const siteToDelete = sitesData[0];

    const { result } = renderHook(() => useDeleteSites(), { wrapper: Providers });
    result.current.mutate({ query: { ids: [siteToDelete.id] } });

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });
  });
});
