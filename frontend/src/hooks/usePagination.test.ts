import usePagination from "./usePagination";

import { hookAct, renderHook } from "@/test-utils";

describe("usePagination", () => {
  const samplePageSize = 50;
  const sampleTotalCount = 200;

  it("initializes the page to 0 when called", () => {
    const { result } = renderHook(() => usePagination(samplePageSize, sampleTotalCount));

    expect(result.current.page).toBe(0);
  });

  it("next and previous page functions work correctly", () => {
    const { result } = renderHook(() => usePagination(samplePageSize, sampleTotalCount));

    hookAct(() => {
      result.current.handleNextClick();
    });

    expect(result.current.page).toBe(1);

    hookAct(() => {
      result.current.handlePreviousClick();
    });

    expect(result.current.page).toBe(0);
  });

  it("should reset page count after page size is changed", () => {
    const { result } = renderHook(() => usePagination(samplePageSize, sampleTotalCount));

    hookAct(() => {
      result.current.handleNextClick();
      result.current.handlePageSizeChange(10);
    });

    expect(result.current.page).toBe(0);
  });
});
