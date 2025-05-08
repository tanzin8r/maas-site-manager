import { http, HttpResponse } from "msw";

import MapSettings from "./MapSettings";

import { userFactory } from "@/mocks/factories";
import { usersResolvers } from "@/testing/resolvers/users";
import { apiUrls } from "@/utils/test-urls";
import { render, screen, setupServer, userEvent, waitFor } from "@/utils/test-utils";

const mockServer = setupServer(usersResolvers.getCurrentUser.handler(userFactory.build({ username: "admin" })));

beforeAll(() => {
  mockServer.listen();
});

beforeEach(() => {
  localStorage.setItem("hasAcceptedOsmTos", JSON.stringify({ admin: false }));
});

afterEach(() => {
  mockServer.resetHandlers();
});

afterAll(() => {
  mockServer.close();
  localStorage.removeItem("hasAcceptedOsmTos");
});

it("shows errors when fetching the current user fails", async () => {
  mockServer.use(
    http.get(apiUrls.currentUser, () => {
      return new HttpResponse(null, { status: 500 });
    }),
  );

  render(<MapSettings />);

  await waitFor(() => {
    expect(screen.getByText("Error while fetching user")).toBeInTheDocument();
  });
});

it("sets the checkbox to checked if the terms have already been accepted", async () => {
  localStorage.setItem("hasAcceptedOsmTos", JSON.stringify({ admin: true }));
  render(<MapSettings />);

  await waitFor(() => {
    expect(
      screen.getByRole("checkbox", {
        name: "I have read and accept the OpenStreetMap term of service and their fair use policy.",
      }),
    ).toBeChecked();
  });
});

it("does not set the checkbox to checked if the terms have not been accepted", async () => {
  render(<MapSettings />);

  await waitFor(() => {
    expect(
      screen.getByRole("checkbox", {
        name: "I have read and accept the OpenStreetMap term of service and their fair use policy.",
      }),
    ).not.toBeChecked();
  });
});

it("updates local storage when the form is submitted", async () => {
  render(<MapSettings />);

  await waitFor(() => {
    expect(
      screen.getByRole("checkbox", {
        name: "I have read and accept the OpenStreetMap term of service and their fair use policy.",
      }),
    ).not.toBeChecked();
  });

  await userEvent.click(
    screen.getByRole("checkbox", {
      name: "I have read and accept the OpenStreetMap term of service and their fair use policy.",
    }),
  );

  await userEvent.click(screen.getByRole("button", { name: "Save" }));

  expect(localStorage.getItem("hasAcceptedOsmTos")).toBe(JSON.stringify({ admin: true }));
});
