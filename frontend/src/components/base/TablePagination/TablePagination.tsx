import type { ChangeEvent } from "react";
import { useMemo, useState, useEffect } from "react";

import { Button, Icon, Input } from "@canonical/react-components";

export type AppPaginationProps = {
  currentPage: number;
  itemsPerPage: number;
  totalItems: number;
  onNextClick: () => void;
  onPreviousClick: () => void;
  setCurrentPage: (x: number) => void;
  isPending: boolean;
};

const TablePagination = ({
  currentPage,
  itemsPerPage,
  totalItems,
  onNextClick,
  onPreviousClick,
  setCurrentPage,
  isPending,
}: AppPaginationProps) => {
  const [pageNumber, setPageNumber] = useState<number | undefined>(currentPage);
  const [error, setError] = useState("");
  const totalPages = useMemo(() => Math.ceil(totalItems / itemsPerPage), [itemsPerPage, totalItems]);

  const handlePageInput = (e: ChangeEvent<HTMLInputElement>) => {
    const { value, valueAsNumber } = e.target;
    if (value) {
      setPageNumber(valueAsNumber);
      if (valueAsNumber > totalPages || valueAsNumber < 1) {
        setError(`${valueAsNumber} is not a valid page`);
      } else {
        setError("");
        setCurrentPage(valueAsNumber);
      }
    } else {
      setError("Enter a page number.");
    }
  };

  useEffect(() => {
    setPageNumber(currentPage);
  }, [currentPage]);

  const handleInputBlur = () => {
    setPageNumber(currentPage);
    setError("");
  };

  const handleNextClick = () => {
    onNextClick();
  };

  const handlePreviousClick = () => {
    onPreviousClick();
  };
  const noItems = totalItems === 0;

  return (
    <nav aria-label="pagination" className="table-pagination">
      <Button
        appearance="base"
        aria-label="previous page"
        disabled={currentPage === 1 || isPending || noItems}
        hasIcon
        onClick={handlePreviousClick}
      >
        <Icon className="u__left-rotate" name="chevron-down" />
      </Button>
      <label>
        <strong>Page</strong>
      </label>
      <Input
        aria-label="current page"
        className="current-page"
        disabled={isPending}
        error={error}
        min={1}
        onBlur={handleInputBlur}
        onChange={handlePageInput}
        type="number"
        value={pageNumber}
      />
      <label>
        <strong className="u-no-wrap"> of {totalPages}</strong>
      </label>
      <Button
        appearance="base"
        aria-label="next page"
        disabled={currentPage === totalPages || isPending || noItems}
        hasIcon
        onClick={handleNextClick}
      >
        <Icon className="u__right-rotate" name="chevron-up" />
      </Button>
    </nav>
  );
};

export default TablePagination;
