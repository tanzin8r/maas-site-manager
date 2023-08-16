import { rest } from "msw";
import { setupServer } from "msw/node";

import RequestsList from "./RequestsList";

import { enrollmentRequestFactory } from "@/mocks/factories";
import { createMockGetEnrollmentRequestsResolver, postEnrollmentRequests } from "@/mocks/resolvers";
import { apiUrls } from "@/utils/test-urls";
import { renderWithMemoryRouter, screen, userEvent, waitFor } from "@/utils/test-utils";

const enrollmentRequest = enrollmentRequestFactory.build({ name: "new-maas-site" });
const enrollmentRequests = [enrollmentRequest, ...enrollmentRequestFactory.buildList(2)];

const mockServer = setupServer(
  rest.get(apiUrls.enrollmentRequests, createMockGetEnrollmentRequestsResolver(enrollmentRequests)),
  postEnrollmentRequests,
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

it("action buttons are disabled if no row is selected", async () => {
  renderWithMemoryRouter(<RequestsList />);

  expect(screen.getByRole("button", { name: /Accept/i })).toBeDisabled();
  expect(screen.getByRole("button", { name: /Deny/i })).toBeDisabled();
});

it("action buttons are enabled if some rows are selected", async () => {
  renderWithMemoryRouter(<RequestsList />);

  await userEvent.click(screen.getByRole("checkbox", { name: /select all/i }));

  await waitFor(() => expect(screen.getByRole("button", { name: /Accept/i })).toBeEnabled());
  expect(screen.getByRole("button", { name: /Deny/i })).toBeEnabled();
});

it("displays a notification and clears selection if a site has been accepted", async () => {
  renderWithMemoryRouter(<RequestsList />);

  // Loading spinner also has "alert" role, wait for page content to load fully.
  await waitFor(() => {
    expect(screen.queryByRole("alert")).not.toBeInTheDocument();
  });

  const requestCheckbox = screen.getByRole("checkbox", { name: `select ${enrollmentRequest.name}` });
  await userEvent.click(requestCheckbox);

  expect(requestCheckbox).toBeChecked();

  await userEvent.click(screen.getByRole("button", { name: /Accept/i }));

  expect(screen.getByRole("alert")).toBeInTheDocument();
  expect(requestCheckbox).not.toBeChecked();
});

it("displays a notification and clears selection if a site has been denied", async () => {
  renderWithMemoryRouter(<RequestsList />);

  await waitFor(() => {
    expect(screen.queryByRole("alert")).not.toBeInTheDocument();
  });

  const requestCheckbox = screen.getByRole("checkbox", { name: `select ${enrollmentRequest.name}` });
  await userEvent.click(requestCheckbox);

  expect(requestCheckbox).toBeChecked();

  await userEvent.click(screen.getByRole("button", { name: /Deny/i }));

  expect(await screen.findByRole("alert")).toBeInTheDocument();
  expect(requestCheckbox).not.toBeChecked();
});
