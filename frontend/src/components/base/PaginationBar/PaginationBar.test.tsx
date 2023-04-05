import PaginationBar from "./PaginationBar";

import { render, screen } from "@/test-utils";

it("should render the PaginationBar component correctly", () => {
  render(
    <PaginationBar
      currentPage={1}
      dataContext="tokens"
      isLoading={false}
      itemsPerPage={10}
      onNextClick={() => {}}
      onPreviousClick={() => {}}
      resetPageCount={() => {}}
      setCurrentPage={() => {}}
      setPageSize={() => {}}
      totalItems={50}
    />,
  );
  expect(screen.getByRole("combobox", { name: /tokens per page/i })).toBeInTheDocument();
  expect(screen.getByRole("navigation", { name: /pagination/i })).toBeInTheDocument();
  expect(screen.getByText(/showing/i)).toBeInTheDocument();
});
