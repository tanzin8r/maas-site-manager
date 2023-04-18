import type { ChangeEvent } from "react";
import { useMemo, useState } from "react";

import { Button, Icon, Input } from "@canonical/react-components";

export type AppPaginationProps = {
  currentPage: number;
  itemsPerPage: number;
  totalItems: number;
  onNextClick: () => void;
  onPreviousClick: () => void;
  setCurrentPage: (x: number) => void;
  isLoading: boolean;
};

const TablePagination = ({
  currentPage,
  itemsPerPage,
  totalItems,
  onNextClick,
  onPreviousClick,
  setCurrentPage,
  isLoading,
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
        setCurrentPage(valueAsNumber - 1);
      }
    } else {
      setPageNumber(undefined);
      setError("Enter a page number.");
    }
  };

  const handleInputBlur = () => {
    setPageNumber(currentPage);
    setError("");
  };

  const handleNextClick = () => {
    onNextClick();
    setPageNumber((prev) => (prev ? prev + 1 : undefined));
  };

  const handlePreviousClick = () => {
    onPreviousClick();
    setPageNumber((prev) => (prev ? prev - 1 : undefined));
  };

  return (
    <nav aria-label="pagination" className="table-pagination">
      <ul>
        <li>
          <Button
            appearance="base"
            aria-label="previous page"
            disabled={currentPage === 1 || isLoading}
            hasIcon
            onClick={handlePreviousClick}
          >
            <Icon className="u__left-rotate" name="chevron-down" />
          </Button>
        </li>
        <span>Page</span>
        <Input
          aria-label="current page"
          className="current-page"
          disabled={isLoading}
          error={error}
          min={1}
          onBlur={handleInputBlur}
          onChange={handlePageInput}
          type="number"
          value={pageNumber}
        />
        <span>of</span>
        <span>{totalPages}</span>
        <li>
          <Button
            appearance="base"
            aria-label="next page"
            disabled={currentPage === totalPages || isLoading}
            hasIcon
            onClick={handleNextClick}
          >
            <Icon className="u__right-rotate" name="chevron-up" />
          </Button>
        </li>
      </ul>
    </nav>
  );
};

export default TablePagination;
