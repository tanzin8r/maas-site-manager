import { postTokens } from "./handlers";

import urls from "@/api/urls";
import { createMockTokensResolver } from "@/mocks/resolvers";
import { createMockPostServer } from "@/mocks/server";

const mockServer = createMockPostServer(urls.tokens, createMockTokensResolver());

beforeAll(() => {
  mockServer.listen();
});
afterEach(() => {
  mockServer.resetHandlers();
});
afterAll(() => {
  mockServer.close();
});

describe("postTokens handler", () => {
  it("requires name, amount and expiration time", async () => {
    // @ts-expect-error
    await expect(postTokens({})).rejects.toThrowError();
  });
});
