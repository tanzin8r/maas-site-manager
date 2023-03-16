import axios from "axios";

import urls from "@/api/urls";
import { tokenFactory } from "@/mocks/factories";
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

describe("mock post tokens server", () => {
  it("returns list of tokens based on the request data", async () => {
    const amount = 1;
    const { expires } = tokenFactory.build({ name: "test", expires: "2021-01-01" });
    const result = await axios.post(urls.tokens, { expires, amount });
    expect(result.data.items).toHaveLength(amount);
    expect(result.data.items[0]).toEqual(expect.objectContaining({ expires }));
  });
});
