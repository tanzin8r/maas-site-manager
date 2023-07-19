import axios from "axios";

import urls from "@/api/urls";
import { durationFactory } from "@/mocks/factories";
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

it("returns list of tokens", async () => {
  const amount = 1;
  const result = await axios.post(urls.tokens, { duration: durationFactory.build(), amount });
  expect(result.data.items).toHaveLength(amount);
});
