/* eslint-disable no-console */
import { lazyWithErrorBoundary } from "./hoc";

import { render, screen } from "@/utils/test-utils";

it("renders the error boundary on component load failure", async () => {
  // Suppress console errors for this test
  const originalConsoleError = console.error;
  console.error = vi.fn();

  const LazyComponent = lazyWithErrorBoundary(() => import("@/mocks/ThrowError"));
  render(<LazyComponent />);
  const errorElement = await screen.findByText(/Custom error message/i);
  expect(errorElement).toBeInTheDocument();

  console.error = originalConsoleError;
});
