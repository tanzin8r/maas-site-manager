import { rest } from "msw";
import { setupServer } from "msw/node";

import { useSites } from "./sites";

import { siteFactory, tokenFactory, userFactory } from "@/mocks/factories";
import {
  createMockGetTokensResolver,
  createMockGetUsersResolver,
  getTokensExport,
  createMockSitesResolver,
} from "@/mocks/resolvers";
import { apiUrls } from "@/utils/test-urls";
import { renderHook, waitFor, Providers } from "@/utils/test-utils";

const sitesData = siteFactory.buildList(2);
const tokensData = tokenFactory.buildList(10);
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
  const { result } = renderHook(() => useSites({ query: { page: 1, size: 2, sort_by: null } }), {
    wrapper: Providers,
  });

  await waitFor(() => expect(result.current.isFetchedAfterMount).toBe(true));

  expect(result.current.data!.items).toEqual(sitesData);
});
