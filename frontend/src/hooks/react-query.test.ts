import { act, renderHook, waitFor } from "@testing-library/react";
import { rest } from "msw";
import { setupServer } from "msw/node";

import { useExportTokensToFileQuery, useSitesQuery, useTokensQuery, useUsersQuery } from "./react-query";

import { siteFactory, tokenFactory, userFactory } from "@/mocks/factories";
import {
  createMockGetTokensResolver,
  createMockGetUsersResolver,
  getTokensExport,
  createMockSitesResolver,
} from "@/mocks/resolvers";
import type * as utils from "@/utils";
import { apiUrls } from "@/utils/test-urls";
import { Providers } from "@/utils/test-utils";

const sitesData = siteFactory.buildList(2);
const tokensData = tokenFactory.buildList(2);
const usersData = userFactory.buildList(2);
const mockServer = setupServer(
  rest.get(apiUrls.sites, createMockSitesResolver(sitesData)),
  rest.get(apiUrls.tokens, createMockGetTokensResolver(tokensData)),
  rest.get(apiUrls.users, createMockGetUsersResolver(usersData)),
  getTokensExport,
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

it("should return sites", async () => {
  const { result } = renderHook(() => useSitesQuery({ page: 1, size: 2, sortBy: null }), {
    wrapper: Providers,
  });

  await waitFor(() => expect(result.current.isFetchedAfterMount).toBe(true));

  expect(result.current.data!.items).toEqual(sitesData);
});

it("should return tokens", async () => {
  const { result } = renderHook(() => useTokensQuery({ page: 1, size: 2 }), { wrapper: Providers });

  await waitFor(() => expect(result.current.isFetchedAfterMount).toBe(true));

  expect(result.current.data!.items).toEqual(tokensData);
});

it("should return users", async () => {
  const { result } = renderHook(() => useUsersQuery({ page: 1, size: 2, sortBy: null }), { wrapper: Providers });

  await waitFor(() => expect(result.current.isFetchedAfterMount).toBe(true));

  expect(result.current.data!.items).toEqual(usersData);
});

it("should finish loading when exporting tokens", async () => {
  vi.mock("@/utils", async (importOriginal) => {
    const original: typeof utils = await importOriginal();
    return {
      ...original,
      saveToFile: vi.fn(),
    };
  });
  const { result } = renderHook(() => useExportTokensToFileQuery(), { wrapper: Providers });

  expect(result.current.isLoading).toBe(false);

  act(() => {
    result.current.exportTokens();
  });
  expect(result.current.isLoading).toBe(true);
  await waitFor(() => expect(result.current.isLoading).toBe(false));
  expect(result.current.error).toBe(null);
});
