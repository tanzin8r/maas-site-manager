import { useState, useEffect } from "react";

import { Button, Col, Row } from "@canonical/react-components";

import PaginationBar from "../base/PaginationBar";

import TokensTable from "./components/TokensTable/TokensTable";

import { useAppContext } from "@/context";
import { useTokensQuery } from "@/hooks/api";
import usePagination from "@/hooks/usePagination";

const DEFAULT_PAGE_SIZE = 50;

const TokensList = () => {
  const { setSidebar } = useAppContext();
  const [totalDataCount, setTotalDataCount] = useState(0);
  const { page, debouncedPage, size, handleNextClick, handlePreviousClick, handlePageSizeChange, setPage } =
    usePagination(DEFAULT_PAGE_SIZE, totalDataCount);

  const { data, isLoading, isFetchedAfterMount } = useTokensQuery({ page: `${debouncedPage}`, size: `${size}` });

  useEffect(() => {
    if (data && "total" in data) {
      setTotalDataCount(data.total);
    }
  }, [data]);

  return (
    <section>
      <Row>
        <Col size={2}>
          <h2 className="p-heading--4">Tokens</h2>
        </Col>
      </Row>
      <Row>
        <Col size={12}>
          <div className="u-flex u-flex--justify-end">
            <Button>Export</Button>
            <Button appearance="negative">Delete</Button>
            <Button className="p-button--positive" onClick={() => setSidebar("createToken")} type="button">
              Generate tokens
            </Button>
          </div>
        </Col>
      </Row>
      <PaginationBar
        currentPage={page + 1}
        dataContext="tokens"
        handlePageSizeChange={handlePageSizeChange}
        isLoading={isLoading}
        itemsPerPage={size}
        onNextClick={handleNextClick}
        onPreviousClick={handlePreviousClick}
        setCurrentPage={setPage}
        totalItems={data?.total || 0}
      />
      <TokensTable data={data} isFetchedAfterMount={isFetchedAfterMount} isLoading={isLoading} />
    </section>
  );
};

export default TokensList;
