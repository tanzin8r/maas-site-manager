import { renderHook, waitFor } from "@testing-library/react";
import urls from "../api/urls";
import { sites } from "../mocks/factories";
import { createMockGetServer } from "../mocks/server";
import { Providers } from "../test-utils";
import { useSitesQuery } from "./api";

const sitesData = sites();
const mockServer = createMockGetServer(urls.sites, sitesData);

beforeAll(() => {
  mockServer.listen();
});
afterEach(() => {
  mockServer.resetHandlers();
});
afterAll(() => {
  mockServer.close();
});

it("should return sites", async () => {
  const { result } = renderHook(() => useSitesQuery(), { wrapper: Providers });

  await waitFor(() => expect(result.current.isFetchedAfterMount).toBe(true));

  expect(result.current.data!.items).toEqual(sitesData.items);
});
