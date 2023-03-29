import * as timezoneMock from "timezone-mock";
import { vi } from "vitest";

import DateTime from "./DateTime";

import { render, screen } from "@/test-utils";

beforeEach(() => {
  vi.useFakeTimers();
  timezoneMock.register("Etc/GMT+8");
});

afterEach(() => {
  timezoneMock.unregister();
  vi.useRealTimers();
});

it("renders time in a correct format", () => {
  render(<DateTime value="2023-01-23T09:36:00.000Z" />);
  expect(screen.getByText("2023-01-23 09:36")).toBeInTheDocument();
});

it("renders invalid time fallback value correctly", () => {
  render(<DateTime value="" />);
  expect(screen.getByText("Invalid time value")).toBeInTheDocument();
});
