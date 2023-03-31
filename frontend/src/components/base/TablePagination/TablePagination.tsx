import type { ChangeEvent } from "react";
import { useMemo } from "react";

import { Button, Icon, Input } from "@canonical/react-components";

export type AppPaginationProps = {
  currentPage: number;
  itemsPerPage: number;
  totalItems: number;
  onNextClick: () => void;
  onPreviousClick: () => void;
  setCurrentPage: (x: number) => void;
};

const TablePagination = ({
  currentPage,
  itemsPerPage,
  totalItems,
  onNextClick,
  onPreviousClick,
  setCurrentPage,
}: AppPaginationProps) => {
  const totalPages = useMemo(() => Math.ceil(totalItems / itemsPerPage), [itemsPerPage, totalItems]);

  const isInputError = currentPage <= 0 || currentPage > totalPages;

  const handlePageInput = (e: ChangeEvent<HTMLInputElement>) => {
    const { valueAsNumber } = e.target;
    // TODO: Handle NaN values
    setCurrentPage(valueAsNumber - 1);
  };

  return (
    <nav aria-label="pagination" className="table-pagination">
      <ul>
        <li>
          <Button
            appearance="base"
            aria-label="previous page"
            disabled={currentPage === 1}
            hasIcon
            onClick={onPreviousClick}
          >
            <Icon className="u__left-rotate" name="chevron-down" />
          </Button>
        </li>
        <span>Page</span>
        <Input
          aria-label="current page"
          className="current-page"
          error={isInputError ? "The entered value is out of range" : undefined}
          min={1}
          onChange={handlePageInput}
          type="number"
          value={currentPage}
        />
        <span>of</span>
        <span>{totalPages}</span>
        <li>
          <Button
            appearance="base"
            aria-label="next page"
            disabled={currentPage === totalPages}
            hasIcon
            onClick={onNextClick}
          >
            <Icon className="u__right-rotate" name="chevron-up" />
          </Button>
        </li>
      </ul>
    </nav>
  );
};

export default TablePagination;
