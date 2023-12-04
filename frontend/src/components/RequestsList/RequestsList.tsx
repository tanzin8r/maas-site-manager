import { Col, Row } from "@canonical/react-components";

import EnrollmentActions from "@/components/EnrollmentActions";
import RequestsTable from "@/components/RequestsTable";
import PaginationBar from "@/components/base/PaginationBar";
import { useRequestsQuery } from "@/hooks/react-query";
import usePagination from "@/hooks/usePagination";

const DEFAULT_PAGE_SIZE = 50;
const Requests: React.FC = () => {
  const { page, debouncedPage, size, handleNextClick, handlePreviousClick, handlePageSizeChange, setPage } =
    usePagination(DEFAULT_PAGE_SIZE);
  const { error, data, isPending } = useRequestsQuery({
    page: debouncedPage,
    size,
  });

  return (
    <section>
      <EnrollmentActions />
      <Row>
        <Col size={12}>
          <PaginationBar
            currentPage={page}
            dataContext="open enrolment requests"
            handlePageSizeChange={handlePageSizeChange}
            isPending={isPending}
            itemsPerPage={size}
            onNextClick={handleNextClick}
            onPreviousClick={handlePreviousClick}
            setCurrentPage={setPage}
            totalItems={data?.total || 0}
          />
        </Col>
        <Col size={12}>
          <RequestsTable data={data} error={error} isPending={isPending} />
        </Col>
      </Row>
    </section>
  );
};

export default Requests;
