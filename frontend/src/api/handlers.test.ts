import { setupServer } from "msw/node";

import { apiClient } from "./api";
import { postEnrollmentRequests, postTokens, getCurrentUser, getTokensExport } from "./handlers";

import { durationFactory } from "@/mocks/factories";
import {
  postTokens as postTokensResolver,
  postEnrollmentRequests as postEnrollmentRequestsResolver,
  getCurrentUser as getCurrentUserResolver,
  getTokensExport as getTokensExportResolver,
  getTokens as getTokensResolver,
} from "@/mocks/resolvers";

const mockServer = setupServer(
  postTokensResolver,
  postEnrollmentRequestsResolver,
  getCurrentUserResolver,
  getTokensExportResolver,
  getTokensResolver,
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

it("requires name, amount and expiration time", async () => {
  // @ts-expect-error Empty objects aren't normally allowed as a prop, but we're trying to force an error here
  await expect(postTokens({})).rejects.toThrow();
  await expect(postTokens({ count: 1, duration: durationFactory.build() })).resolves.toBeDefined();
});

it("requires ids and accept values", async () => {
  // @ts-expect-error Empty objects aren't normally allowed as a prop, but we're trying to force an error here
  await expect(postEnrollmentRequests({})).rejects.toThrow();
  await expect(postEnrollmentRequests({ ids: [], accept: false })).resolves.toEqual(undefined);
  await expect(postEnrollmentRequests({ ids: [], accept: true })).resolves.toEqual(undefined);
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

it("paginates the tokens export if called without explicit IDs", async () => {
  const getTokenCount = vi.spyOn(apiClient.default, "getV1TokensGet");
  // should not call getTokenCount with ID. Can export from first page using only "getExportV1TokensExportGet"
  await getTokensExport({ id: [1] });
  expect(getTokenCount).not.toHaveBeenCalled();

  // should call getTokenCount as it needs to calculate the pages
  await getTokensExport({ id: [] });
  expect(getTokenCount).toHaveBeenCalledTimes(1);
});
