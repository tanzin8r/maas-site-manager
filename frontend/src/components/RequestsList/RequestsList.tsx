import { ContentSection } from "@canonical/maas-react-components";

import EnrollmentActions from "@/components/EnrollmentActions";
import RequestsTable from "@/components/RequestsTable";
import PaginationBar from "@/components/base/PaginationBar";
import { useRequestsQuery } from "@/hooks/react-query";
import usePagination from "@/hooks/usePagination";

const DEFAULT_PAGE_SIZE = 50;
const Requests: React.FC = () => {
  const { page, debouncedPage, size, handlePageSizeChange, setPage } = usePagination(DEFAULT_PAGE_SIZE);
  const { error, data, isPending } = useRequestsQuery({
    page: debouncedPage,
    size,
  });

  return (
    <ContentSection>
      <ContentSection.Header>
        <EnrollmentActions />
        <PaginationBar
          currentPage={page}
          dataContext="open enrolment requests"
          handlePageSizeChange={handlePageSizeChange}
          isPending={isPending}
          itemsPerPage={size}
          setCurrentPage={setPage}
          totalItems={data?.total || 0}
        />
      </ContentSection.Header>
      <ContentSection.Content>
        <RequestsTable currentPage={page} data={data} error={error} isPending={isPending} pageSize={size} />
      </ContentSection.Content>
    </ContentSection>
  );
};

export default Requests;
