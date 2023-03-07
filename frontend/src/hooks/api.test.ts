import { renderHook, waitFor } from "@testing-library/react";

import urls from "../api/urls";
import { siteFactory } from "../mocks/factories";
import { createMockSitesResolver } from "../mocks/resolvers";
import { createMockGetServer } from "../mocks/server";
import { Providers } from "../test-utils";

import { useSitesQuery } from "./api";

const sitesData = siteFactory.buildList(2);
const mockServer = createMockGetServer(urls.sites, createMockSitesResolver(sitesData));

beforeAll(() => {
  mockServer.listen();
});
afterEach(() => {
  mockServer.resetHandlers();
});
afterAll(() => {
  mockServer.close();
});

it("should return sites", async () => {
  const { result } = renderHook(() => useSitesQuery({ page: "0", size: "2" }), { wrapper: Providers });

  await waitFor(() => expect(result.current.isFetchedAfterMount).toBe(true));

  expect(result.current.data!.items).toEqual(sitesData);
});
