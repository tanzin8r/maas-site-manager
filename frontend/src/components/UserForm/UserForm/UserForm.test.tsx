import type { RenderResult } from "@testing-library/react";
import { rest } from "msw";

import UserForm from "./UserForm";

import { UserSelectionContext } from "@/context/UserSelectionContext";
import { userFactory } from "@/mocks/factories";
import { createMockGetUserResolver } from "@/mocks/resolvers";
import { apiUrls } from "@/utils/test-urls";
import { render, screen, setupServer, userEvent, waitFor } from "@/utils/test-utils";

const user = userFactory.build({ is_admin: true });
const mockServer = setupServer(rest.get(`${apiUrls.users}/:id`, createMockGetUserResolver([user])));

const renderEditForm = (): RenderResult => {
  const setSelected = vi.fn();
  return render(
    <UserSelectionContext.Provider value={{ selected: user.id, setSelected }}>
      <UserForm type="edit" />
    </UserSelectionContext.Provider>,
  );
};

beforeAll(() => {
  mockServer.listen();
});

afterEach(() => {
  mockServer.resetHandlers();
});

afterAll(() => {
  mockServer.close();
});

it("prefills data for a user when editing", async () => {
  renderEditForm();

  await waitFor(() => {
    expect(screen.getByRole("heading", { name: `Edit ${user.username}` })).toBeInTheDocument();
  });

  await waitFor(async () => {
    expect(screen.getByRole("textbox", { name: "Username" })).toHaveValue(user.username);
  });
  expect(screen.getByRole("textbox", { name: "Full name (optional)" })).toHaveValue(user.full_name);
  expect(screen.getByRole("textbox", { name: "Email address" })).toHaveValue(user.email);
  expect(screen.getByRole("checkbox", { name: "MAAS Site Manager administrator" })).toBeChecked();
});

it("enables the submit button only when values have been changed while editing", async () => {
  renderEditForm();

  // Wait for form to load
  await waitFor(async () => {
    expect(screen.getByRole("button", { name: "Save" })).toBeDisabled();
  });

  await userEvent.clear(screen.getByRole("textbox", { name: "Full name (optional)" }));

  expect(screen.getByRole("button", { name: "Save" })).toBeEnabled();
});

it("makes the confirm_password field required if the password field has been filled in while editing", async () => {
  renderEditForm();

  // Wait for form to load
  await waitFor(() => {
    expect(screen.getByLabelText("Password (again)")).not.toBeRequired();
  });

  await userEvent.type(screen.getByLabelText("Password"), "testpassword");

  expect(screen.getByLabelText("Password (again)")).toBeRequired();
});

it("requires the password fields when adding a user", () => {
  render(<UserForm type="add" />);

  expect(screen.getByLabelText("Password")).toBeRequired();
  expect(screen.getByLabelText("Password (again)")).toBeRequired();
});

it("enables the submit button when all required fields are filled in and valid when editing a user", async () => {
  render(<UserForm type="add" />);

  expect(screen.getByRole("button", { name: "Add user" })).toBeDisabled();

  await userEvent.type(screen.getByRole("textbox", { name: "Username" }), "user1");
  await userEvent.type(screen.getByRole("textbox", { name: "Email address" }), "user1@example.com");
  await userEvent.type(screen.getByLabelText("Password"), "testpassword");

  // Ensure form is still disabled
  expect(screen.getByRole("button", { name: "Add user" })).toBeDisabled();

  await userEvent.type(screen.getByLabelText("Password (again)"), "testpassword");

  expect(screen.getByRole("button", { name: "Add user" })).toBeEnabled();
});

it("displays an error if a username with invalid characters is entered", async () => {
  render(<UserForm type="add" />);

  await userEvent.type(screen.getByRole("textbox", { name: "Username" }), "not a valid username");
  await userEvent.tab();

  expect(screen.getByText(/Usernames must contain letters, digits and @\/.\/\+\/-\/_ only/i)).toBeInTheDocument();
});

it("displays an error if a username over 150 characters in length is entered", async () => {
  render(<UserForm type="add" />);

  // 151 characters long, max is 150
  const tooLong = "A".repeat(151);

  await userEvent.type(screen.getByRole("textbox", { name: "Username" }), tooLong);
  await userEvent.tab();

  await waitFor(() => {
    expect(screen.getByText(/Username must be 150 characters or less/i)).toBeInTheDocument();
  });
});

it("displays an error if no username is entered", async () => {
  render(<UserForm type="add" />);

  await userEvent.click(screen.getByRole("textbox", { name: "Username" }));
  await userEvent.tab();

  expect(screen.getByText(/Username is required/i)).toBeInTheDocument();
});

it("displays an error if an invalid email address is entered", async () => {
  render(<UserForm type="add" />);

  await userEvent.type(screen.getByRole("textbox", { name: "Email address" }), "not a valid email address");
  await userEvent.tab();

  expect(screen.getByText(/Must be a valid email address/i)).toBeInTheDocument();
});

it("displays an error if a password less than 8 characters in length is entered", async () => {
  render(<UserForm type="add" />);

  // 151 characters long, max is 150
  const tooShort = "AAAA";

  await userEvent.type(screen.getByLabelText("Password"), tooShort);
  await userEvent.tab();

  expect(screen.getByText(/Password must be at least 8 characters/i)).toBeInTheDocument();
});

it("displays an error if a password over 100 characters in length is entered", async () => {
  render(<UserForm type="add" />);

  // 101 characters long, max is 100
  const tooLong = "A".repeat(101);

  await userEvent.type(screen.getByLabelText("Password"), tooLong);
  await userEvent.tab();

  await waitFor(() => {
    expect(screen.getByText(/Password must be 100 characters or less/i)).toBeInTheDocument();
  });
});

it("displays an error if the password confirmation field does not match the given password", async () => {
  render(<UserForm type="add" />);
  await userEvent.type(screen.getByLabelText("Password"), "aValidPassword");
  await userEvent.type(screen.getByLabelText("Password (again)"), "notTheSamePassword");
  await userEvent.tab();

  expect(
    screen.getByText(/New passwords do not match. Please ensure the new passwords are the same./i),
  ).toBeInTheDocument();
});
