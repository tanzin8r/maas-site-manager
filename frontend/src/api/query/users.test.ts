import { setupServer } from "msw/node";

import { useUsers } from "./users";

import { userFactory } from "@/mocks/factories";
import { usersResolvers } from "@/testing/resolvers/users";
import { renderHook, waitFor, Providers } from "@/utils/test-utils";

const usersData = userFactory.buildList(2);
const mockServer = setupServer(usersResolvers.listUsers.handler(usersData));

beforeAll(() => {
  mockServer.listen();
});
afterEach(() => {
  mockServer.resetHandlers();
});
afterAll(() => {
  mockServer.close();
});

it("should return users", async () => {
  const { result } = renderHook(() => useUsers({ query: { page: 1, size: 2, sort_by: null } }), { wrapper: Providers });

  await waitFor(() => expect(result.current.isFetchedAfterMount).toBe(true));

  expect(result.current.data!.items).toEqual(usersData);
});
