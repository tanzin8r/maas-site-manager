import { useState } from "react";

import useDebouncedValue from "./useDebouncedValue";

function usePagination(pageSize: number, totalItems: number) {
  const [page, setPage] = useState(0);
  const [size, setSize] = useState(pageSize);
  const debouncedPage = useDebouncedValue(page);

  const handleNextClick = () => {
    const maxPage = totalItems > 0 ? totalItems / size : 1;
    setPage((prev) => (prev >= maxPage ? maxPage : prev + 1));
  };

  const handlePreviousClick = () => {
    setPage((prev) => (prev === 0 ? 0 : prev - 1));
  };

  const resetPageCount = () => setPage(0);

  const handlePageSizeChange = (size: number) => {
    setSize(size);
    resetPageCount();
  };

  return {
    page: page,
    size,
    setPage,
    debouncedPage: debouncedPage,
    handleNextClick,
    handlePreviousClick,
    handlePageSizeChange,
    totalItems,
  };
}

export default usePagination;
