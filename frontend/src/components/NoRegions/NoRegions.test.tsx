import NoRegions from "./NoRegions";

import urls from "@/api/urls";
import { enrollmentRequestFactory } from "@/mocks/factories";
import { createMockGetEnrollmentRequestsResolver } from "@/mocks/resolvers";
import { createMockGetServer } from "@/mocks/server";
import { getByTextContent, renderWithMemoryRouter, screen, waitFor } from "@/test-utils";

describe("open enrollment requests available", () => {
  const enrollmentRequests = enrollmentRequestFactory.buildList(2);
  const mockServer = createMockGetServer(
    urls.enrollmentRequests,
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

  it("should display 'no enrolled regions' text", () => {
    renderWithMemoryRouter(<NoRegions />);

    expect(screen.getByText(/no enroled maas regions/i)).toBeInTheDocument();
  });
  it("should display link to enrollment docs", () => {
    renderWithMemoryRouter(<NoRegions />);

    expect(
      screen.getByRole("link", { name: /learn more about the enrolment process in the documentation\./i }),
    ).toBeInTheDocument();
  });

  it("should display a link to the request page if there are open requests", async () => {
    renderWithMemoryRouter(<NoRegions />);

    await waitFor(() =>
      expect(
        screen.getByRole("link", {
          name: /go to requests page/i,
        }),
      ).toBeInTheDocument(),
    );
  });

  it("should display the amount of open enrollment requests", async () => {
    renderWithMemoryRouter(<NoRegions />);

    await waitFor(() =>
      expect(
        getByTextContent(new RegExp("You have 2 open enrolment requests, inspect them in the Requests page.", "i")),
      ).toBeInTheDocument(),
    );
  });
});

describe("no open enrollment requests available", () => {
  const enrollmentRequests = enrollmentRequestFactory.buildList(0);
  const mockServer = createMockGetServer(
    urls.enrollmentRequests,
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

  it("should display a link to the tokens page", async () => {
    renderWithMemoryRouter(<NoRegions />);

    await waitFor(() =>
      expect(
        screen.getByRole("link", {
          name: /go to tokens page/i,
        }),
      ).toBeInTheDocument(),
    );
  });

  it("should display a link to enrollment process docs", () => {
    renderWithMemoryRouter(<NoRegions />);

    expect(
      screen.getByRole("link", {
        name: new RegExp("Learn more about the enrolment process in the documentation.", "i"),
      }),
    ).toBeInTheDocument();
  });
});
