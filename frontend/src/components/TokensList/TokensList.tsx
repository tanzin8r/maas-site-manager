import { useState } from "react";

import { Button, Col, Row } from "@canonical/react-components";

import PaginationBar from "../base/PaginationBar";

import TokensTable from "./components/TokensTable/TokensTable";

import { useAppContext } from "@/context";
import { useTokensQuery } from "@/hooks/api";
import useDebouncedValue from "@/hooks/useDebouncedValue";

const DEFAULT_PAGE_SIZE = 50;

const TokensList = () => {
  const { setSidebar } = useAppContext();
  const [page, setPage] = useState(0);
  const [size, setSize] = useState(DEFAULT_PAGE_SIZE);
  const debouncedPageNumber = useDebouncedValue(page);

  const { data, isLoading, isFetchedAfterMount } = useTokensQuery({ page: `${debouncedPageNumber}`, size: `${size}` });

  const handleNextClick = () => {
    const maxPage = data?.total ? data?.total / size : 1;
    setPage((prev) => (prev >= maxPage ? maxPage : prev + 1));
  };

  const handlePreviousClick = () => {
    setPage((prev) => (prev === 0 ? 0 : prev - 1));
  };

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
        itemsPerPage={size}
        onNextClick={handleNextClick}
        onPreviousClick={handlePreviousClick}
        resetPageCount={() => setPage(0)}
        setCurrentPage={setPage}
        setPageSize={setSize}
        totalItems={data?.total || 0}
      />
      <TokensTable data={data} isFetchedAfterMount={isFetchedAfterMount} isLoading={isLoading} />
    </section>
  );
};

export default TokensList;
