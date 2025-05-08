import { http, HttpResponse } from "msw";

import PasswordUpdate from "./PasswordUpdate";

import { usersResolvers } from "@/testing/resolvers/users";
import { apiUrls } from "@/utils/test-urls";
import { render, screen, setupServer, userEvent, waitFor } from "@/utils/test-utils";

const mockServer = setupServer(usersResolvers.updateCurrentUserPassword.handler());

beforeAll(() => {
  mockServer.listen();
});

afterEach(() => {
  mockServer.resetHandlers();
});

afterAll(() => {
  mockServer.close();
});

it("should render password update form", () => {
  render(<PasswordUpdate />);

  expect(screen.getByRole("form", { name: /update password/i })).toBeInTheDocument();
  expect(screen.getByLabelText("Current password")).toBeInTheDocument();
  expect(screen.getByLabelText("New password")).toBeInTheDocument();
  expect(screen.getByLabelText("New password (again)")).toBeInTheDocument();
});

it("submit button is disabled on page mount", async () => {
  render(<PasswordUpdate />);

  expect(screen.getByRole("button", { name: /save/i })).toBeAriaDisabled();
});

it("Input helper texts are displayed", () => {
  render(<PasswordUpdate />);

  expect(
    screen.getByText(/if you can't remember your current password, ask an admin to change your password\./i),
  ).toBeInTheDocument();
  expect(screen.getByText(/enter the same password as before, for verification/i)).toBeInTheDocument();
});

it("displays a validation error if current password field is cleared", async () => {
  render(<PasswordUpdate />);

  const currentPasswordField = screen.getByLabelText("Current password");

  await userEvent.type(currentPasswordField, "some text");
  await userEvent.clear(currentPasswordField);
  await userEvent.tab();

  expect(screen.getByText(/current password is required/i)).toBeInTheDocument();
});

it("displays a validation error is passwords don't match", async () => {
  render(<PasswordUpdate />);

  const newPasswordField = screen.getByLabelText("New password");
  const confirmPasswordField = screen.getByLabelText("New password (again)");

  await userEvent.type(newPasswordField, "abc");
  await userEvent.type(confirmPasswordField, "def");
  await userEvent.tab();

  expect(screen.getByText(/new passwords must match/i)).toBeInTheDocument();
});

it("enables submit button only when all fields are filled correctly", async () => {
  render(<PasswordUpdate />);

  const currentPasswordField = screen.getByLabelText("Current password");
  const newPasswordField = screen.getByLabelText("New password");
  const confirmPasswordField = screen.getByLabelText("New password (again)");
  const submitBtn = screen.getByRole("button", { name: /save/i });

  // fill current password field
  await userEvent.type(currentPasswordField, "currentPassword");
  expect(submitBtn).toBeAriaDisabled();
  // fill new password field
  await userEvent.type(newPasswordField, "newPassword");
  expect(submitBtn).toBeAriaDisabled();
  // fill confirm password field with different password
  await userEvent.type(confirmPasswordField, "differentPassword");
  expect(submitBtn).toBeAriaDisabled();

  // fill confirm password field with same as new password field
  await userEvent.clear(confirmPasswordField);
  await userEvent.type(confirmPasswordField, "newPassword");
  expect(submitBtn).not.toBeAriaDisabled();
});

it("shows a success message when password is updated", async () => {
  render(<PasswordUpdate />);

  await userEvent.type(screen.getByLabelText("Current password"), "currentPassword");
  await userEvent.type(screen.getByLabelText("New password"), "newPassword");
  await userEvent.type(screen.getByLabelText("New password (again)"), "newPassword");

  await userEvent.click(screen.getByRole("button", { name: /Save/i }));

  expect(screen.getByText(/Your password has been updated/i)).toBeInTheDocument();
});

it("shows an error message when password update fails", async () => {
  mockServer.use(
    http.patch(`${apiUrls.currentUser}/password`, () => {
      return new HttpResponse(null, { status: 400 });
    }),
  );

  render(<PasswordUpdate />);

  await userEvent.type(screen.getByLabelText("Current password"), "currentPassword");
  await userEvent.type(screen.getByLabelText("New password"), "newPassword");
  await userEvent.type(screen.getByLabelText("New password (again)"), "newPassword");

  await userEvent.click(screen.getByRole("button", { name: /Save/i }));

  expect(screen.getByText(/Error while updating password/i)).toBeInTheDocument();
});

it("clears form fields after successful password update", async () => {
  render(<PasswordUpdate />);

  await userEvent.type(screen.getByLabelText("Current password"), "currentPassword");
  await userEvent.type(screen.getByLabelText("New password"), "newPassword");
  await userEvent.type(screen.getByLabelText("New password (again)"), "newPassword");

  await userEvent.click(screen.getByRole("button", { name: /Save/i }));

  await waitFor(() => {
    expect(screen.getByText(/Your password has been updated/i)).toBeInTheDocument();
  });

  expect(screen.getByLabelText("Current password")).toHaveValue("");
  expect(screen.getByLabelText("New password")).toHaveValue("");
  expect(screen.getByLabelText("New password (again)")).toHaveValue("");
});
