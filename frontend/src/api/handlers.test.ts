import { setupServer } from "msw/node";

import { postEnrollmentRequests, postTokens } from "./handlers";

import { durationFactory } from "@/mocks/factories";
import {
  postTokens as postTokensResolver,
  postEnrollmentRequests as postEnrollmentRequestsResolver,
} from "@/mocks/resolvers";

const mockServer = setupServer(postTokensResolver, postEnrollmentRequestsResolver);

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
    await expect(postTokens({ amount: 1, duration: durationFactory.build() })).resolves.toEqual(
      expect.objectContaining({
        items: expect.any(Array),
      }),
    );
  });
});

describe("postEnrollmentRequests handler", () => {
  it("requires ids and accept values", async () => {
    // @ts-expect-error
    await expect(postEnrollmentRequests({})).rejects.toThrowError();
    await expect(postEnrollmentRequests({ ids: [], accept: false })).resolves.toEqual("");
    await expect(postEnrollmentRequests({ ids: [], accept: true })).resolves.toEqual("");
  });
});
