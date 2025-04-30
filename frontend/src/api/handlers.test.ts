import { setupServer } from "msw/node";

import { apiClient } from "./api";
import { getTokensExport } from "./handlers";

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

it("paginates the tokens export if called without explicit IDs", async () => {
  const getTokenCount = vi.spyOn(apiClient.default, "getV1TokensGet");
  // should not call getTokenCount with ID. Can export from first page using only "getExportV1TokensExportGet"
  await getTokensExport({ id: [1] });
  expect(getTokenCount).not.toHaveBeenCalled();

  // should call getTokenCount as it needs to calculate the pages
  await getTokensExport({ id: [] });
  expect(getTokenCount).toHaveBeenCalledTimes(1);
});
