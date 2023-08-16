import { rest } from "msw";

import NoSites from "./NoSites";

import { enrollmentRequestFactory } from "@/mocks/factories";
import { createMockGetEnrollmentRequestsResolver } from "@/mocks/resolvers";
import { createMockGetServer } from "@/mocks/server";
import { apiUrls } from "@/utils/test-urls";
import { getByTextContent, renderWithMemoryRouter, screen, waitFor } from "@/utils/test-utils";

const renderComponent = () =>
  renderWithMemoryRouter(
    // render inside a table to avoid warnings about invalid DOM nesting
    <table>
      <NoSites />
    </table>,
  );

const enrollmentRequests = enrollmentRequestFactory.buildList(2);
const mockServer = createMockGetServer(
  apiUrls.enrollmentRequests,
  createMockGetEnrollmentRequestsResolver(enrollmentRequests),
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

it("should display 'no enrolled sites' text", () => {
  renderComponent();
  expect(screen.getByText(/no enroled maas sites/i)).toBeInTheDocument();
});
it("should display link to enrollment docs", () => {
  renderComponent();

  expect(
    screen.getByRole("link", { name: /learn more about the enrolment process in the documentation\./i }),
  ).toBeInTheDocument();
});

it("should display a link to the request page if there are open requests", async () => {
  renderComponent();
  await waitFor(() =>
    expect(
      screen.getByRole("link", {
        name: /go to requests page/i,
      }),
    ).toBeInTheDocument(),
  );
});

it("should display the amount of open enrollment requests", async () => {
  renderComponent();
  await waitFor(() =>
    expect(
      getByTextContent(new RegExp("You have 2 open enrolment requests, inspect them in the Requests page.", "i")),
    ).toBeInTheDocument(),
  );
});

it("should display a link to the tokens page if no enrollment requests are open", async () => {
  mockServer.resetHandlers(rest.get(apiUrls.enrollmentRequests, createMockGetEnrollmentRequestsResolver([])));
  renderComponent();
  await waitFor(() =>
    expect(
      screen.getByRole("link", {
        name: /go to tokens page/i,
      }),
    ).toBeInTheDocument(),
  );
});
