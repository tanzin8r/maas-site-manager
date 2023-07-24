import { rest } from "msw";
import { setupServer } from "msw/node";

import DeleteUser from "./DeleteUser";

import urls from "@/api/urls";
import { UserSelectionContext } from "@/context";
import { userFactory } from "@/mocks/factories";
import { createMockDeleteUserResolver, createMockGetUserResolver } from "@/mocks/resolvers";
import { render, screen, userEvent, waitFor } from "@/utils/test-utils";

const mockUser = userFactory.build({ username: "abc123", id: 2 });

const mockServer = setupServer(
  rest.delete(`${urls.users}/:id`, createMockDeleteUserResolver()),
  rest.get(`${urls.users}/:id`, createMockGetUserResolver([mockUser])),
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

describe("DeleteUser", () => {
  const renderDeleteForm = () => {
    const setSelectedUserId = vi.fn();
    return render(
      <UserSelectionContext.Provider value={{ selectedUserId: mockUser.id, setSelectedUserId }}>
        <DeleteUser />
      </UserSelectionContext.Provider>,
    );
  };

  it("displays the user delete dialog", async () => {
    renderDeleteForm();

    await waitFor(() =>
      expect(screen.getByRole("heading", { name: new RegExp(`delete ${mockUser.username}`, "i") })).toBeInTheDocument(),
    );
    expect(screen.getByRole("heading", { name: new RegExp(`delete ${mockUser.username}`, "i") })).toBeInTheDocument();
    expect(
      screen.getByRole("textbox", {
        name: new RegExp(`type ${mockUser.username} to confirm`, "i"),
      }),
    ).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /delete/i })).toBeInTheDocument();
  });

  it("displays the username as the input placeholder", async () => {
    renderDeleteForm();
    await waitFor(() => expect(screen.getByPlaceholderText(mockUser.username)).toBeInTheDocument());
  });

  it("disables delete button on mount", async () => {
    renderDeleteForm();

    await waitFor(() => expect(screen.getByRole("button", { name: /delete/i })).toBeDisabled());
  });

  it("only enables delete button when username is typed", async () => {
    renderDeleteForm();

    const input = await waitFor(() =>
      screen.getByRole("textbox", {
        name: new RegExp(`type ${mockUser.username} to confirm`, "i"),
      }),
    );
    // type random string
    await userEvent.type(input, "test");
    await expect(screen.getByRole("button", { name: /delete/i })).toBeDisabled();

    // type correct username
    await userEvent.clear(input);
    await userEvent.type(input, mockUser.username);
    await expect(screen.getByRole("button", { name: /delete/i })).toBeEnabled();
  });
});
