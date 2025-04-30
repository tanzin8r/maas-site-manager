import { rest } from "msw";

import EnrollmentActions from "./EnrollmentActions";

import { createMockPostEnrollmentRequestsResolver } from "@/mocks/resolvers";
import { apiUrls } from "@/utils/test-urls";
import { renderWithMemoryRouter, screen, setupServer, userEvent, within } from "@/utils/test-utils";

const mockServer = setupServer(rest.post(apiUrls.enrollmentRequests, createMockPostEnrollmentRequestsResolver()));

vi.mock("@/context", async () => {
  const actual = await vi.importActual("@/context");
  return {
    ...actual!,
    useRowSelection: () => ({
      rowSelection: {
        "1": true,
        "2": true,
      },
    }),
  };
});

beforeAll(() => {
  mockServer.listen();
});

afterEach(() => {
  mockServer.resetHandlers();
});

afterAll(() => {
  mockServer.close();
});

it("displays enrollment action buttons", () => {
  renderWithMemoryRouter(<EnrollmentActions />);

  expect(screen.getByRole("button", { name: /Deny/i })).toBeInTheDocument();
  expect(screen.getByRole("button", { name: /Accept/i })).toBeInTheDocument();
});

it("can display an error message on request error", async () => {
  mockServer.use(
    rest.post(apiUrls.enrollmentRequests, (req, res, ctx) => {
      return res(ctx.status(400));
    }),
  );
  renderWithMemoryRouter(<EnrollmentActions />);

  await userEvent.click(screen.getByRole("button", { name: /Accept/i }));

  expect(
    within(screen.getByRole("alert")).getByText(/There was an error processing enrollment request/i),
  ).toBeInTheDocument();
});
