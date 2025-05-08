import { setupServer } from "msw/node";

import { useSites } from "./sites";

import { siteFactory, tokenFactory, userFactory } from "@/mocks/factories";
import { sitesResolvers } from "@/testing/resolvers/sites";
import { tokensResolvers } from "@/testing/resolvers/tokens";
import { usersResolvers } from "@/testing/resolvers/users";
import { renderHook, waitFor, Providers } from "@/utils/test-utils";

const sitesData = siteFactory.buildList(2);
const tokensData = tokenFactory.buildList(10);
const usersData = userFactory.buildList(2);
const mockServer = setupServer(
  sitesResolvers.listSites.handler(sitesData),
  tokensResolvers.listTokens.handler(tokensData),
  usersResolvers.listUsers.handler(usersData),
  tokensResolvers.exportTokens.handler(),
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
