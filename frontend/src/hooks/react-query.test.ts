import { renderHook, waitFor } from "@testing-library/react";
import { rest } from "msw";
import { setupServer } from "msw/node";

import { useSitesQuery, useTokensQuery, useUsersQuery } from "./react-query";

import urls from "@/api/urls";
import { siteFactory, tokenFactory, userFactory } from "@/mocks/factories";
import { createMockGetTokensResolver, createMockGetUsersResolver, createMockSitesResolver } from "@/mocks/resolvers";
import { Providers } from "@/utils/test-utils";

const sitesData = siteFactory.buildList(2);
const tokensData = tokenFactory.buildList(2);
const usersData = userFactory.buildList(2);
const mockServer = setupServer(
  rest.get(urls.sites, createMockSitesResolver(sitesData)),
  rest.get(urls.tokens, createMockGetTokensResolver(tokensData)),
  rest.get(urls.users, createMockGetUsersResolver(usersData)),
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
  const { result } = renderHook(() => useSitesQuery({ page: "1", size: "2", sort_by: null }), { wrapper: Providers });

  await waitFor(() => expect(result.current.isFetchedAfterMount).toBe(true));

  expect(result.current.data!.items).toEqual(sitesData);
});

it("should return tokens", async () => {
  const { result } = renderHook(() => useTokensQuery({ page: "1", size: "2" }), { wrapper: Providers });

  await waitFor(() => expect(result.current.isFetchedAfterMount).toBe(true));

  expect(result.current.data!.items).toEqual(tokensData);
});

it("should return users", async () => {
  const { result } = renderHook(() => useUsersQuery({ page: "1", size: "2", sort_by: null }), { wrapper: Providers });

  await waitFor(() => expect(result.current.isFetchedAfterMount).toBe(true));

  expect(result.current.data!.items).toEqual(usersData);
});
