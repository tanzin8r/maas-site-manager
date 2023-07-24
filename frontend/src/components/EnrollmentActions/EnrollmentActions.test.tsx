import EnrollmentActions from "./EnrollmentActions";

import type * as apiHooks from "@/hooks/react-query";
import { render, screen, within } from "@/utils/test-utils";

const enrollmentRequestsMutationMock = vi.fn();

it("displays enrollment action buttons", () => {
  render(<EnrollmentActions />);

  expect(screen.getByRole("button", { name: /Deny/i })).toBeInTheDocument();
  expect(screen.getByRole("button", { name: /Accept/i })).toBeInTheDocument();
});

it("can display an error message on request error", () => {
  vi.mock("@/hooks/react-query", async (importOriginal) => {
    const original: typeof apiHooks = await importOriginal();
    return {
      ...original,
      useEnrollmentRequestsMutation: () => ({ mutate: enrollmentRequestsMutationMock, isError: true }),
    };
  });
  render(<EnrollmentActions />);

  expect(
    within(screen.getByRole("alert")).getByText(/There was an error processing enrolment request/i),
  ).toBeInTheDocument();
});
