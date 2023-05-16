import { useState, useEffect } from "react";

import { Button, Col, Row, Notification } from "@canonical/react-components";
import pluralize from "pluralize";

import TokensTable from "./components/TokensTable/TokensTable";

import docsUrls from "@/base/docsUrls";
import ExternalLink from "@/components/ExternalLink";
import PaginationBar from "@/components/base/PaginationBar";
import { useAppContext } from "@/context";
import { useRowSelectionContext } from "@/context/RowSelectionContext";
import { useDeleteTokensMutation, useTokensQuery } from "@/hooks/react-query";
import usePagination from "@/hooks/usePagination";

const DEFAULT_PAGE_SIZE = 50;

const TokensList = () => {
  const { setSidebar } = useAppContext();
  const { rowSelection, setRowSelection } = useRowSelectionContext("tokens");
  const [totalDataCount, setTotalDataCount] = useState(0);
  const [deleteNotification, setDeleteNotification] = useState("");
  const { page, debouncedPage, size, handleNextClick, handlePreviousClick, handlePageSizeChange, setPage } =
    usePagination(DEFAULT_PAGE_SIZE, totalDataCount);

  const { error, data, isLoading, isSuccess } = useTokensQuery({
    page: `${debouncedPage}`,
    size: `${size}`,
  });

  const handleTokenDeleteSuccess = () => {
    const deletedTokenCount = Object.keys(rowSelection).length;
    setDeleteNotification(
      `${deletedTokenCount === 1 ? "An" : ""} ${pluralize(
        "enrollment token",
        deletedTokenCount,
        deletedTokenCount > 1,
      )} ${deletedTokenCount === 1 ? "was" : "were"} deleted.`,
    );
    setRowSelection({});
  };
  const tokensDeleteMutation = useDeleteTokensMutation({ onSuccess: handleTokenDeleteSuccess });

  useEffect(() => {
    if (data && "total" in data) {
      setTotalDataCount(data.total);
    }
  }, [data]);

  const handleTokenDelete = () => {
    const selectedIds = isSuccess ? Object.keys(rowSelection).map((_, idx) => Number(data.items[idx].id)) : [];
    tokensDeleteMutation.mutate(selectedIds);
  };

  return (
    <section className="tokens-list">
      {deleteNotification ? (
        <Row>
          <Col size={12}>
            <Notification severity="information" title="Deleted">
              {deleteNotification}
            </Notification>
          </Col>
        </Row>
      ) : null}
      <header className="tokens-list-header" id="tokens-list-header">
        <Row>
          <Col size={12}>
            <p className="tokens-list-instructions">
              Follow the enrolment steps outlined in the{" "}
              {/* TODO: Update link once documentation is live https://warthogs.atlassian.net/browse/MAASENG-1585 */}
              <ExternalLink to={docsUrls.enrollmentRequest}>documentation</ExternalLink> to enrol new regions. Once an
              enrolment request was made use the following certificate data to compare against the certificate shown in
              the enrolment request:
            </p>
            {/* TODO: Add actual certificate here once endpoint is ready https://warthogs.atlassian.net/browse/MAASENG-1584 */}
            <code className="tokens-list-certificate">
              <span>CN:</span>
              <span>sitemanager.example.com</span>
              <span>Expiration date:</span>
              <span>Thu, 29 Jul. 2035</span>
              <span>Fingerprint:</span>
              <span>15cf96e8bad3eea3ef3c10badcd88f66fe236e0de99027451120bc7cd69c0012</span>
              <span>Issued by:</span>
              <span>Let's Encrypt</span>
            </code>
          </Col>
        </Row>
        <Row>
          <Col size={12}>
            <div className="u-flex u-flex--justify-end">
              <Button disabled={!Object.keys(rowSelection).length}>Export</Button>
              <Button appearance="negative" disabled={!Object.keys(rowSelection).length} onClick={handleTokenDelete}>
                Delete
              </Button>
              <Button className="p-button--positive" onClick={() => setSidebar("createToken")} type="button">
                Generate tokens
              </Button>
            </div>
          </Col>
        </Row>
        <PaginationBar
          currentPage={page}
          dataContext="tokens"
          handlePageSizeChange={handlePageSizeChange}
          isLoading={isLoading}
          itemsPerPage={size}
          onNextClick={handleNextClick}
          onPreviousClick={handlePreviousClick}
          setCurrentPage={setPage}
          totalItems={data?.total || 0}
        />
      </header>
      <TokensTable data={data} error={error} isLoading={isLoading} />
    </section>
  );
};

export default TokensList;
