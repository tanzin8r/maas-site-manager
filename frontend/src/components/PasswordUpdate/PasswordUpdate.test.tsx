import PasswordUpdate from "./PasswordUpdate";

import { render, screen, userEvent } from "@/test-utils";

describe("PasswordUpdate", () => {
  it("should render password update form", () => {
    render(<PasswordUpdate />);

    expect(screen.getByRole("form", { name: /update password/i })).toBeInTheDocument();
    expect(screen.getByLabelText("Current password")).toBeInTheDocument();
    expect(screen.getByLabelText("New password")).toBeInTheDocument();
    expect(screen.getByLabelText("New password (again)")).toBeInTheDocument();
  });

  it("submit button is disabled on page mount", async () => {
    render(<PasswordUpdate />);

    await expect(screen.getByRole("button", { name: /save/i })).toBeDisabled();
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
    await expect(submitBtn).toBeDisabled();
    // fill new password field
    await userEvent.type(newPasswordField, "newPassword");
    await expect(submitBtn).toBeDisabled();
    // fill confirm password field with different password
    await userEvent.type(confirmPasswordField, "differentPassword");
    await expect(submitBtn).toBeDisabled();

    // fill confirm password field with same as new password field
    await userEvent.clear(confirmPasswordField);
    await userEvent.type(confirmPasswordField, "newPassword");
    await expect(submitBtn).toBeEnabled();
  });
});
