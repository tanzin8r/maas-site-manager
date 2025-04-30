import { rest } from "msw";
import { setupServer } from "msw/node";

import { useExportTokensToFileQuery } from "./react-query";

import { siteFactory, tokenFactory, userFactory } from "@/mocks/factories";
import {
  createMockGetTokensResolver,
  createMockGetUsersResolver,
  getTokensExport,
  createMockSitesResolver,
} from "@/mocks/resolvers";
import type * as utils from "@/utils";
import { apiUrls } from "@/utils/test-urls";
import { act, renderHook, waitFor, Providers } from "@/utils/test-utils";

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

it("should finish loading when exporting tokens", async () => {
  vi.mock("@/utils", async (importOriginal) => {
    const original: typeof utils = await importOriginal();
    return {
      ...original,
      saveToFile: vi.fn(),
    };
  });
  const { result } = renderHook(() => useExportTokensToFileQuery({ id: [] }), { wrapper: Providers });

  expect(result.current.isPending).toBe(false);

  act(() => {
    result.current.exportTokens({});
  });
  expect(result.current.isPending).toBe(true);
  await waitFor(() => expect(result.current.isPending).toBe(false));
  expect(result.current.error).toBe(null);
});
