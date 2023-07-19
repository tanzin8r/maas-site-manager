import { setupServer } from "msw/node";

import { postEnrollmentRequests, postTokens, getCurrentUser } from "./handlers";

import { durationFactory } from "@/mocks/factories";
import {
  postTokens as postTokensResolver,
  postEnrollmentRequests as postEnrollmentRequestsResolver,
  getCurrentUser as getCurrentUserResolver,
} from "@/mocks/resolvers";

const mockServer = setupServer(postTokensResolver, postEnrollmentRequestsResolver, getCurrentUserResolver);

beforeAll(() => {
  mockServer.listen();
});
afterEach(() => {
  mockServer.resetHandlers();
});
afterAll(() => {
  mockServer.close();
});

it("requires name, amount and expiration time", async () => {
  // @ts-expect-error
  await expect(postTokens({})).rejects.toThrowError();
  await expect(postTokens({ amount: 1, duration: durationFactory.build() })).resolves.toEqual(
    expect.objectContaining({
      items: expect.any(Array),
    }),
  );
});

it("requires ids and accept values", async () => {
  // @ts-expect-error
  await expect(postEnrollmentRequests({})).rejects.toThrowError();
  await expect(postEnrollmentRequests({ ids: [], accept: false })).resolves.toEqual("");
  await expect(postEnrollmentRequests({ ids: [], accept: true })).resolves.toEqual("");
});

it("returns the user object", async () => {
  await expect(getCurrentUser()).resolves.toEqual(
    expect.objectContaining({
      id: expect.any(Number),
      username: expect.any(String),
      email: expect.any(String),
      full_name: expect.any(String),
    }),
  );
});
