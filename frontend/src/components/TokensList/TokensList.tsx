import { ContentSection, ExternalLink, MainToolbar } from "@canonical/maas-react-components";
import { Button, Notification } from "@canonical/react-components";
import pluralize from "pluralize";

import TokensTable from "./components/TokensTable/TokensTable";

import ErrorMessage from "@/components/ErrorMessage/ErrorMessage";
import PaginationBar from "@/components/base/PaginationBar";
import RemoveButton from "@/components/base/RemoveButton";
import docsUrls from "@/config/docsUrls";
import { useAppLayoutContext } from "@/context";
import { useRowSelection } from "@/context/RowSelectionContext/RowSelectionContext";
import { useDeleteTokensMutation, useTokensQuery, useExportTokensToFileQuery } from "@/hooks/react-query";
import usePagination from "@/hooks/usePagination";

const DEFAULT_PAGE_SIZE = 50;

const TokensList = () => {
  const { setSidebar } = useAppLayoutContext();
  const { page, debouncedPage, size, handlePageSizeChange, setPage } = usePagination(DEFAULT_PAGE_SIZE);
  const { rowSelection, clearRowSelection } = useRowSelection("tokens", { currentPage: page, pageSize: size });

  const { error, data, isPending } = useTokensQuery({
    page: debouncedPage,
    size,
  });

  const {
    error: exportTokensError,
    isPending: isExportTokensLoading,
    exportTokens,
  } = useExportTokensToFileQuery({ id: Object.keys(rowSelection).map((id) => Number(id)) });

  const tokensDeleteMutation = useDeleteTokensMutation({
    onSuccess: clearRowSelection,
  });

  const handleTokenDelete = () => {
    const selectedIds = Object.keys(rowSelection).map((id) => Number(id));
    tokensDeleteMutation.mutate(selectedIds);
  };

  const deletedTokensCount = tokensDeleteMutation.variables?.length;
  return (
    <ContentSection>
      {tokensDeleteMutation.isSuccess && deletedTokensCount ? (
        <Notification severity="information" title="Deleted">
          {`${deletedTokensCount === 1 ? "An" : ""} ${pluralize(
            "enrollment token",
            deletedTokensCount,
            deletedTokensCount > 1,
          )} ${deletedTokensCount === 1 ? "was" : "were"} deleted.`}
        </Notification>
      ) : null}
      {exportTokensError ? (
        <Notification severity="negative" title="Error">
          <ErrorMessage error={exportTokensError} />
        </Notification>
      ) : null}
      {tokensDeleteMutation.isError ? (
        <Notification severity="negative" title="Error">
          <ErrorMessage
            defaultMessage="An error occured while deleting the tokens"
            error={tokensDeleteMutation.error}
          />
        </Notification>
      ) : null}
      <ContentSection.Header className="tokens-list-header">
        <p className="tokens-list-instructions">
          Follow the enrolment steps outlined in the{" "}
          {/* TODO: Update link once documentation is live https://warthogs.atlassian.net/browse/MAASENG-1585 */}
          <ExternalLink to={docsUrls.enrollmentRequest}>documentation</ExternalLink> to enrol new sites. Once an
          enrolment request was made use the following certificate data to compare against the certificate shown in the
          enrolment request:
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
        <MainToolbar>
          <MainToolbar.Controls>
            <Button disabled={isExportTokensLoading} onClick={exportTokens}>
              Export
            </Button>
            <RemoveButton disabled={!Object.keys(rowSelection).length} label="Delete" onClick={handleTokenDelete} />
            <Button className="p-button--positive" onClick={() => setSidebar("createToken")} type="button">
              Generate tokens
            </Button>
          </MainToolbar.Controls>
        </MainToolbar>
        <PaginationBar
          currentPage={page}
          dataContext="tokens"
          handlePageSizeChange={handlePageSizeChange}
          isPending={isPending}
          itemsPerPage={size}
          setCurrentPage={setPage}
          totalItems={data?.total || 0}
        />
      </ContentSection.Header>
      <TokensTable data={data} error={error} isPending={isPending} />
    </ContentSection>
  );
};

export default TokensList;
