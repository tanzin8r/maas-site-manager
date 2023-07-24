import usePagination from "./usePagination";

import { renderHook, act } from "@/utils/test-utils";

const samplePageSize = 50;
const sampleTotalCount = 200;

it("initializes the page to 1 when called", () => {
  const { result } = renderHook(() => usePagination(samplePageSize, sampleTotalCount));

  expect(result.current.page).toBe(1);
});

it("next and previous page functions work correctly", async () => {
  const { result } = renderHook(() => usePagination(samplePageSize, sampleTotalCount));
  await act(() => {
    result.current.handleNextClick();
  });
  expect(result.current.page).toBe(2);
  await act(() => {
    result.current.handlePreviousClick();
  });
  expect(result.current.page).toBe(1);
});

it("should reset page count after page size is changed", async () => {
  const { result } = renderHook(() => usePagination(samplePageSize, sampleTotalCount));

  await act(() => {
    result.current.handleNextClick();
    result.current.handlePageSizeChange(10);
  });

  expect(result.current.page).toBe(1);
});
