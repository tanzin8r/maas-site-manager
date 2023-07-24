import useDebouncedValue from "./useDebouncedValue";

import { act, renderHook } from "@/utils/test-utils";

beforeEach(() => {
  vi.useFakeTimers();
});

afterEach(() => {
  vi.useRealTimers();
});

it("returns debounced value", async () => {
  const { result, rerender } = renderHook(({ value }) => useDebouncedValue(value), {
    initialProps: {
      value: "value",
    },
  });
  expect(result.current).toBe("value");
  rerender({ value: "new-value" });
  await act(async () => {
    await vi.runAllTimersAsync();
  });
  expect(result.current).toBe("new-value");
});

it("accepts custom delay", async () => {
  const { result, rerender } = renderHook(({ value, delay }) => useDebouncedValue(value, delay), {
    initialProps: {
      value: "value",
      delay: 5,
    },
  });
  expect(result.current).toBe("value");
  rerender({ value: "new-value", delay: 5 });
  await act(async () => {
    await vi.advanceTimersByTimeAsync(5);
  });
  expect(result.current).toBe("new-value");
});
