import { http, HttpResponse } from "msw";
import { setupServer } from "msw/node";

import PersonalDetailsUpdate from "./PersonalDetailsUpdate";

import { userFactory } from "@/mocks/factories";
import { usersResolvers } from "@/testing/resolvers/users";
import { apiUrls } from "@/utils/test-urls";
import { render, screen, userEvent, waitFor } from "@/utils/test-utils";

const mockServer = setupServer(
  usersResolvers.getCurrentUser.handler(userFactory.build({ username: "admin", email: "admin@example.com" })),
  usersResolvers.updateCurrentUser.handler(),
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

it("renders correctly", () => {
  render(<PersonalDetailsUpdate />);

  expect(screen.getByRole("form", { name: "update personal details" })).toBeInTheDocument();
  expect(screen.getByRole("textbox", { name: "Username" })).toBeInTheDocument();
  expect(screen.getByRole("textbox", { name: "Full name (optional)" })).toBeInTheDocument();
  expect(screen.getByRole("textbox", { name: "Email Address" })).toBeInTheDocument();
});

it("displays required validation for Username and Email fields", async () => {
  render(<PersonalDetailsUpdate />);

  const usernameInput = screen.getByRole("textbox", { name: "Username" });
  const emailInput = screen.getByRole("textbox", { name: "Email Address" });

  await userEvent.clear(usernameInput);
  await userEvent.type(usernameInput, "test");
  await userEvent.clear(usernameInput);
  await userEvent.tab();

  expect(screen.getByText("Username is required")).toBeInTheDocument();

  await userEvent.clear(emailInput);
  await userEvent.type(emailInput, "test");
  await userEvent.clear(emailInput);
  await userEvent.tab();

  expect(screen.getByText("Email address is required")).toBeInTheDocument();
});

it("disables submit button on mount", async () => {
  render(<PersonalDetailsUpdate />);
  expect(screen.getByRole("button", { name: /save/i })).toBeAriaDisabled();
});

it("displays email validation error for invalid input", async () => {
  render(<PersonalDetailsUpdate />);
  const emailInput = screen.getByRole("textbox", { name: "Email Address" });

  // Wait for the form to pre-fill first
  await waitFor(() => expect(emailInput).toHaveValue("admin@example.com"));

  await userEvent.clear(emailInput);
  await userEvent.type(emailInput, "test");
  await userEvent.tab();

  expect(screen.getByText("Email address is invalid")).toBeInTheDocument();
});

it("enables submit button when all required fields are filled", async () => {
  render(<PersonalDetailsUpdate />);
  const usernameInput = screen.getByRole("textbox", { name: "Username" });
  const emailInput = screen.getByRole("textbox", { name: "Email Address" });

  await userEvent.clear(usernameInput);
  await userEvent.clear(emailInput);
  await userEvent.type(usernameInput, "test");
  await userEvent.type(emailInput, "mail@example.com");

  expect(screen.getByRole("button", { name: /save/i })).not.toBeAriaDisabled();
});

it("renders page with prefilled inputs", async () => {
  render(<PersonalDetailsUpdate />);

  await waitFor(async () => {
    expect(
      screen.getByRole("textbox", {
        name: /username/i,
      }),
    ).toHaveValue("admin");
  });
  expect(
    screen.getByRole("textbox", {
      name: /email address/i,
    }),
  ).toHaveValue("admin@example.com");
});

it("displays a success notification on successful update", async () => {
  render(<PersonalDetailsUpdate />);

  const usernameInput = screen.getByRole("textbox", { name: "Username" });
  await userEvent.clear(usernameInput);
  await userEvent.type(usernameInput, "test");

  await userEvent.click(screen.getByRole("button", { name: /save/i }));

  await waitFor(() => {
    expect(
      screen.getByRole("heading", {
        name: /details updated/i,
      }),
    ).toBeInTheDocument();
  });
  expect(screen.getByText(/your details were updated successfully/i)).toBeInTheDocument();
});

it("displays an error notification on unsuccessful update", async () => {
  mockServer.use(
    http.patch(`${apiUrls.users}/:id`, () => {
      return new HttpResponse(null, { status: 400 });
    }),
  );

  render(<PersonalDetailsUpdate />);

  const usernameInput = screen.getByRole("textbox", { name: "Username" });
  await userEvent.clear(usernameInput);
  await userEvent.type(usernameInput, "test");

  await userEvent.click(screen.getByRole("button", { name: /save/i }));

  expect(screen.getByText(/error while updating details/i)).toBeInTheDocument();
});
