import type { ChangeEvent } from "react";
import { useMemo } from "react";

import { Select } from "@canonical/react-components";

import ControlsBar from "@/components/base/ControlsBar";
import type { AppPaginationProps } from "@/components/base/TablePagination/TablePagination";
import TablePagination from "@/components/base/TablePagination/TablePagination";

export type PaginationBarProps = AppPaginationProps & {
  handlePageSizeChange: (size: number) => void;
  dataContext: string;
  setCurrentPage: (page: number) => void;
  isPending: boolean;
};

const PaginationBar = ({
  currentPage,
  itemsPerPage,
  totalItems,
  onNextClick,
  onPreviousClick,
  handlePageSizeChange,
  dataContext,
  setCurrentPage,
  isPending,
}: PaginationBarProps) => {
  const pageCounts = useMemo(() => [20, 30, 50], []);
  const pageOptions = useMemo(
    () => pageCounts.map((pageCount) => ({ label: `${pageCount}/page`, value: pageCount })),
    [pageCounts],
  );

  const handleSizeChange = (e: ChangeEvent<HTMLSelectElement>) => {
    const { value } = e.target;
    handlePageSizeChange(Number(value));
  };

  const getDisplayedDataCount = () => {
    const totalPages = Math.ceil(totalItems / itemsPerPage);

    if (currentPage === totalPages) {
      return itemsPerPage - (totalPages * itemsPerPage - totalItems);
    } else if (currentPage < totalPages) {
      return itemsPerPage;
    } else {
      return 0;
    }
  };

  return (
    <ControlsBar>
      <ControlsBar.Left>
        Showing {getDisplayedDataCount()} out of {totalItems} {dataContext}
      </ControlsBar.Left>
      <ControlsBar.Right>
        <TablePagination
          currentPage={currentPage}
          isPending={isPending}
          itemsPerPage={itemsPerPage}
          onNextClick={onNextClick}
          onPreviousClick={onPreviousClick}
          setCurrentPage={setCurrentPage}
          totalItems={totalItems}
        />
        <Select
          aria-label="Items per page"
          className="u-no-margin--bottom"
          name="Items per page"
          onChange={handleSizeChange}
          options={pageOptions}
          value={itemsPerPage}
        />
      </ControlsBar.Right>
    </ControlsBar>
  );
};

export default PaginationBar;
