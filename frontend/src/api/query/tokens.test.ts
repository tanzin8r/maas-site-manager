import { setupServer } from "msw/node";

import { useCreateTokens, useDeleteTokens, useExportTokens, useTokenCount, useTokens } from "./tokens";

import type { TokensPostRequest } from "@/apiclient";
import { tokenFactory } from "@/mocks/factories";
import { tokensResolvers } from "@/testing/resolvers/tokens";
import { renderHook, waitFor, Providers } from "@/utils/test-utils";

const tokensData = tokenFactory.buildList(10);
const mockServer = setupServer(
  tokensResolvers.listTokens.handler(tokensData),
  tokensResolvers.createTokens.handler(),
  tokensResolvers.exportTokens.handler(tokensData),
  tokensResolvers.deleteTokens.handler(),
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

describe("useTokens", () => {
  it("should return tokens data", async () => {
    const { result } = renderHook(
      () =>
        useTokens({
          query: {
            page: 1,
            size: 5,
          },
        }),
      { wrapper: Providers },
    );

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    expect(result.current.data?.items).toEqual(tokensData.slice(0, 5));
    expect(result.current.data?.total).toBe(10);
  });
});

describe("useTokenCount", () => {
  it("should return correct count", async () => {
    const { result } = renderHook(() => useTokenCount(), { wrapper: Providers });
    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });
    expect(result.current.data).toBe(tokensData.length);
  });

  it("should return 0 when no zones exist", async () => {
    mockServer.use(tokensResolvers.listTokens.handler([]));
    const { result } = renderHook(() => useTokenCount(), { wrapper: Providers });
    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });
    expect(result.current.data).toBe(0);
  });
});

describe("useCreateTokens", () => {
  it("should create a new token", async () => {
    const newToken: TokensPostRequest = {
      count: 2,
      duration: "12 hours",
    };

    const { result } = renderHook(() => useCreateTokens(), { wrapper: Providers });
    result.current.mutate({ body: newToken });

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    expect(result.current.data?.items).toBeDefined();
    expect(result.current.data?.items.length).toBe(2);
  });
});

describe("useExportTokens", () => {
  it("should export tokens by ids", async () => {
    const { result } = renderHook(
      () =>
        useExportTokens({
          query: {
            id: [tokensData[0].id, tokensData[1].id],
          },
        }),
      { wrapper: Providers },
    );

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    const expectedCSV = [
      "id,value,expired,created",
      ...tokensData.slice(0, 2).map((t) => `${t.id},${t.value},${t.expired},${t.created}`),
    ].join("\n");

    expect(result.current.isError).toBe(false);
    expect(result.current.data).toBeDefined();
    await waitFor(() => expect(result.current.data).not.toBeNull());
    expect(result.current.data).toEqual(expectedCSV);
  });

  it("should export all tokens when no ids are provided", async () => {
    const { result } = renderHook(
      () =>
        useExportTokens({
          query: {
            page: 1,
            size: 10,
          },
        }),
      { wrapper: Providers },
    );

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    const expectedCSV = [
      "id,value,expired,created",
      ...tokensData.map((t) => `${t.id},${t.value},${t.expired},${t.created}`),
    ].join("\n");

    expect(result.current.isError).toBe(false);
    expect(result.current.data).toBeDefined();
    await waitFor(() => expect(result.current.data).not.toBeNull());
    expect(result.current.data).toEqual(expectedCSV);
  });
});

describe("useDeleteTokens", () => {
  it("should delete tokens by id", async () => {
    const { result } = renderHook(() => useDeleteTokens(), { wrapper: Providers });
    result.current.mutate({ query: { ids: [1, 2] } });

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });
  });
});
