import LoginForm from "./LoginForm";

import { renderWithMemoryRouter, screen, userEvent, waitFor } from "@/utils/test-utils";

it("renders", () => {
  renderWithMemoryRouter(<LoginForm />);

  expect(screen.getByRole("form", { name: "Login" })).toBeInTheDocument();
});

it("displays an error if the username input is left empty", async () => {
  renderWithMemoryRouter(<LoginForm />);

  const emailInput = screen.getByRole("textbox", { name: "Email" });

  await userEvent.type(emailInput, "test");
  await userEvent.clear(emailInput);
  await userEvent.click(screen.getByRole("form"));

  expect(screen.getByText(/Please enter an email address/)).toBeInTheDocument();
});

it("displays an error if the password input is left empty", async () => {
  renderWithMemoryRouter(<LoginForm />);

  const passwordInput = screen.getByLabelText("Password");

  await userEvent.type(passwordInput, "test");
  await userEvent.clear(passwordInput);
  await userEvent.tab();

  await waitFor(() => expect(screen.getByText(/Please enter a password/)).toBeInTheDocument());
});

it("disables the 'Login' button if a username and password are not present", async () => {
  renderWithMemoryRouter(<LoginForm />);

  const emailInput = screen.getByRole("textbox", { name: "Email" });
  const passwordInput = screen.getByLabelText("Password");
  const loginButton = screen.getByRole("button", { name: "Login" });

  expect(loginButton).toBeAriaDisabled();

  await userEvent.type(emailInput, "uname@provider.com");
  expect(loginButton).toBeAriaDisabled();

  await userEvent.clear(emailInput);
  await userEvent.type(passwordInput, "pword");
  expect(loginButton).toBeAriaDisabled();

  await userEvent.type(emailInput, "uname@provider.com");
  expect(loginButton).not.toBeAriaDisabled();
});
