import { useLogin } from "./auth";

import { authResolvers } from "@/testing/resolvers/auth";
import { Providers, renderHook, setupServer, waitFor } from "@/utils/test-utils";

const mockServer = setupServer(authResolvers.login.handler());

beforeAll(() => {
  mockServer.listen();
});

afterEach(() => {
  mockServer.resetHandlers();
});

afterAll(() => {
  mockServer.close();
});

describe("useLogin", () => {
  it("should return an access token when login is successful", async () => {
    const { result } = renderHook(() => useLogin(), { wrapper: Providers });
    const login = result.current.mutateAsync;
    const { access_token } = await login({ body: { username: "admin", password: "admin" } });
    await waitFor(() => expect(access_token).toBeDefined());
  });
});
