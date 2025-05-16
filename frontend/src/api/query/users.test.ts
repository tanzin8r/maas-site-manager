import { setupServer } from "msw/node";

import {
  useAddUser,
  useChangePassword,
  useCurrentUser,
  useDeleteUser,
  useEditCurrentUser,
  useEditUser,
  useUser,
  useUsers,
} from "./users";

import type { UsersPasswordPatchRequest, UsersPatchRequest, UsersPostRequest } from "@/apiclient";
import { userFactory } from "@/mocks/factories";
import { usersResolvers } from "@/testing/resolvers/users";
import { Providers, renderHook, waitFor } from "@/utils/test-utils";

const usersData = userFactory.buildList(2);
const mockServer = setupServer(
  usersResolvers.listUsers.handler(usersData),
  usersResolvers.getUser.handler(usersData),
  usersResolvers.getCurrentUser.handler(usersData[0]),
  usersResolvers.createUser.handler(),
  usersResolvers.updateUser.handler(),
  usersResolvers.updateCurrentUser.handler(),
  usersResolvers.updateCurrentUserPassword.handler(),
  usersResolvers.deleteUser.handler(),
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

describe("useUsers", () => {
  it("should return users data", async () => {
    const { result } = renderHook(
      () =>
        useUsers({
          query: {
            page: 1,
            size: 2,
          },
        }),
      { wrapper: Providers },
    );

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    expect(result.current.data?.items).toEqual(usersData);
  });
});

describe("useUser", () => {
  it("should return the correct user", async () => {
    const expectedUser = usersData[0];
    const { result } = renderHook(() => useUser({ path: { id: expectedUser.id } }), {
      wrapper: Providers,
    });

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    expect(result.current.data).toEqual(expectedUser);
  });

  it("should return error if user does not exist", async () => {
    const { result } = renderHook(() => useUser({ path: { id: 99 } }), {
      wrapper: Providers,
    });

    await waitFor(() => {
      expect(result.current.isError).toBe(true);
    });
  });

  it("should not fetch when disabled", async () => {
    const { result } = renderHook(() => useUser({ path: { id: 1 } }, false), {
      wrapper: Providers,
    });

    // Since the query is disabled, it should not start loading
    expect(result.current.isLoading).toBe(false);
    expect(result.current.isFetching).toBe(false);
  });
});

describe("useCurrentUser", () => {
  it("should return current user data", async () => {
    const { result } = renderHook(() => useCurrentUser(), { wrapper: Providers });

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    expect(result.current.data).toEqual(usersData[0]);
  });
});

describe("useAddUser", () => {
  it("should add a new user", async () => {
    const newUser: UsersPostRequest = {
      full_name: "New User",
      username: "newUser",
      email: "new@example.com",
      password: "password123",
      confirm_password: "password123",
    };

    const { result } = renderHook(() => useAddUser(), { wrapper: Providers });
    result.current.mutate({ body: newUser });

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    expect(result.current.data?.id).toBeDefined();
  });
});

describe("useEditUser", () => {
  it("should update an existing user", async () => {
    const updatedData: UsersPatchRequest = {
      username: "updatedUser",
      email: "updated@example.com",
    };

    const { result } = renderHook(() => useEditUser(), { wrapper: Providers });
    result.current.mutate({ body: updatedData, path: { id: 1 } });

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    expect(result.current.data?.username).toBe(updatedData.username);
  });
});

describe("useEditCurrentUser", () => {
  it("should update the current user", async () => {
    const updateData: UsersPatchRequest = {
      username: "updatedCurrentUser",
      email: "updatedcurrent@example.com",
    };

    const { result } = renderHook(() => useEditCurrentUser(), { wrapper: Providers });
    result.current.mutate({ body: updateData });

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    expect(result.current.data?.username).toBe(updateData.username);
  });
});

describe("useChangePassword", () => {
  it("should change password successfully", async () => {
    const passwordData: UsersPasswordPatchRequest = {
      current_password: "oldPassword",
      new_password: "newPassword",
      confirm_password: "newPassword",
    };

    const { result } = renderHook(() => useChangePassword(), { wrapper: Providers });
    result.current.mutate({ body: passwordData });

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });
  });
});

describe("useDeleteUser", () => {
  it("should delete a user", async () => {
    const { result } = renderHook(() => useDeleteUser(), { wrapper: Providers });
    result.current.mutate({ path: { id: 1 } });

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });
  });
});
