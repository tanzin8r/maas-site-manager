import type { ChangeEvent } from "react";
import { useMemo } from "react";

import { Col, Row, Select } from "@canonical/react-components";

import type { AppPaginationProps } from "@/components/base/TablePagination/TablePagination";
import TablePagination from "@/components/base/TablePagination/TablePagination";

type TokensTableControlProps = AppPaginationProps & {
  handlePageSizeChange: (size: number) => void;
  dataContext: string;
  setCurrentPage: (page: number) => void;
  isLoading: boolean;
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
  isLoading,
}: TokensTableControlProps) => {
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
    <Row className="pagination-bar">
      <Col medium={6} size={7} small={4}>
        <p className="pagination-bar__description">
          Showing {getDisplayedDataCount()} out of {totalItems} {dataContext}
        </p>
      </Col>
      <Col medium={3} size={3} small={4}>
        <TablePagination
          currentPage={currentPage}
          isLoading={isLoading}
          itemsPerPage={itemsPerPage}
          onNextClick={onNextClick}
          onPreviousClick={onPreviousClick}
          setCurrentPage={setCurrentPage}
          totalItems={totalItems}
        />
      </Col>
      <Col medium={3} size={2} small={4}>
        <Select
          aria-label="Tokens per page"
          name="Tokens per page"
          onChange={handleSizeChange}
          options={pageOptions}
          value={itemsPerPage}
        />
      </Col>
    </Row>
  );
};

export default PaginationBar;
