import { rest } from "msw";
import { setupServer } from "msw/node";

import { useTokens } from "./tokens";

import { tokenFactory } from "@/mocks/factories";
import { createMockGetTokensResolver } from "@/mocks/resolvers";
import { apiUrls } from "@/utils/test-urls";
import { renderHook, waitFor, Providers } from "@/utils/test-utils";

const tokensData = tokenFactory.buildList(10);
const mockServer = setupServer(rest.get(apiUrls.tokens, createMockGetTokensResolver(tokensData)));

beforeAll(() => {
  mockServer.listen();
});
afterEach(() => {
  mockServer.resetHandlers();
});
afterAll(() => {
  mockServer.close();
});

it("should return tokens", async () => {
  const { result } = renderHook(() => useTokens({ query: { page: 1, size: 2 } }), { wrapper: Providers });

  await waitFor(() => expect(result.current.isFetchedAfterMount).toBe(true));

  expect(result.current.data!.items).toEqual([tokensData[0], tokensData[1]]);
});
