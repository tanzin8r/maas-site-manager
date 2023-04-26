import { useState, useEffect } from "react";

import { Accordion, Button, Col, Row, Notification } from "@canonical/react-components";
import pluralize from "pluralize";
import { Link } from "react-router-dom";

import TokensTable from "./components/TokensTable/TokensTable";

import docsUrls from "@/base/docsUrls";
import { routesConfig } from "@/base/routesConfig";
import ExternalLink from "@/components/ExternalLink";
import PaginationBar from "@/components/base/PaginationBar";
import { useAppContext } from "@/context";
import { useDeleteTokensMutation, useTokensQuery } from "@/hooks/api";
import usePagination from "@/hooks/usePagination";

const DEFAULT_PAGE_SIZE = 50;

const TokensList = () => {
  const { setSidebar, rowSelection, setRowSelection } = useAppContext();
  const [totalDataCount, setTotalDataCount] = useState(0);
  const [deleteNotification, setDeleteNotification] = useState("");
  const { page, debouncedPage, size, handleNextClick, handlePreviousClick, handlePageSizeChange, setPage } =
    usePagination(DEFAULT_PAGE_SIZE, totalDataCount);

  const { data, isLoading, isFetchedAfterMount, isSuccess } = useTokensQuery({
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
    const selectedIds = isSuccess ? Object.keys(rowSelection).map((_, idx) => data.items[idx].id) : [];
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
            <p>Follow the enrolment steps to enrol new regions:</p>
            <Accordion
              sections={[
                {
                  content: (
                    <ol>
                      <li>
                        Generate single use tokens by clicking <strong>Generate tokens</strong>
                      </li>
                      <li>
                        Install site-manager-agent alongside a MAAS region controller
                        <br />
                        <code>snap install site-manager-agent</code>
                      </li>
                      <li>
                        In the site-manager-agent CLI paste the snippet below. Download the{" "}
                        <ExternalLink to={docsUrls.configFile}>
                          {/* TODO: Update link once documentation is live https://warthogs.atlassian.net/browse/MAASENG-1585 */}
                          optional config file
                        </ExternalLink>{" "}
                        to provide additional data for a specific MAAS region.
                        <br />
                        <code>site-manager-agent enrol location.host $ENROLMENT_TOKEN [$CONFIG_FILE_PATH]</code>
                        <br />
                        {/* TODO: Add certificate here once endpoint is ready https://warthogs.atlassian.net/browse/MAASENG-1584 */}
                      </li>
                      <li>
                        Accept the incoming request in the <Link to={routesConfig.requests.path}>Requests page</Link>
                      </li>
                    </ol>
                  ),
                  title: "Enrolment steps",
                },
              ]}
            />
            <p>
              Learn more about the enrolment process and bulk enrolment{" "}
              {/* TODO: Update link once documentation is live https://warthogs.atlassian.net/browse/MAASENG-1585 */}
              <ExternalLink to={docsUrls.baseDocsLink}>in the documentation</ExternalLink>.
            </p>
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
      </header>
      <TokensTable data={data} isFetchedAfterMount={isFetchedAfterMount} isLoading={isLoading} />
    </section>
  );
};

export default TokensList;
