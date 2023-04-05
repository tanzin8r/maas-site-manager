import { vi } from "vitest";

import TablePagination from "./TablePagination";

import { render, screen, userEvent } from "@/test-utils";

it("should render pagination component correctly", () => {
  render(
    <TablePagination
      currentPage={1}
      isLoading={false}
      itemsPerPage={10}
      onNextClick={() => {}}
      onPreviousClick={() => {}}
      setCurrentPage={vi.fn(() => {})}
      totalItems={50}
    />,
  );
  expect(screen.getByRole("navigation", { name: /pagination/i })).toBeInTheDocument();
});

it("should render previous button as disabled on first page", () => {
  render(
    <TablePagination
      currentPage={1}
      isLoading={false}
      itemsPerPage={10}
      onNextClick={() => {}}
      onPreviousClick={() => {}}
      setCurrentPage={() => {}}
      totalItems={50}
    />,
  );
  expect(screen.getByRole("button", { name: /previous/i })).toBeDisabled();
});

it("should render next button as disabled on last page", () => {
  render(
    <TablePagination
      currentPage={1}
      isLoading={false}
      itemsPerPage={10}
      onNextClick={() => {}}
      onPreviousClick={() => {}}
      setCurrentPage={() => {}}
      totalItems={1}
    />,
  );
  expect(screen.getByRole("button", { name: /next/i })).toBeDisabled();
});

it("next and previous buttons work as expected", async () => {
  const onPreviousClick = vi.fn(() => {});
  const onNextClick = vi.fn(() => {});
  render(
    <TablePagination
      currentPage={2}
      isLoading={false}
      itemsPerPage={10}
      onNextClick={onNextClick}
      onPreviousClick={onPreviousClick}
      setCurrentPage={() => {}}
      totalItems={50}
    />,
  );
  const previousButton = screen.getByRole("button", { name: /previous page/i });
  await userEvent.click(previousButton);
  expect(onPreviousClick).toHaveBeenCalled();

  const nextButton = screen.getByRole("button", { name: /next page/i });
  await userEvent.click(nextButton);
  expect(onNextClick).toHaveBeenCalled();
});

it("should have a numeric input showing the current page", () => {
  const currentPage = 1;
  render(
    <TablePagination
      currentPage={currentPage}
      isLoading={false}
      itemsPerPage={10}
      onNextClick={() => {}}
      onPreviousClick={() => {}}
      setCurrentPage={() => {}}
      totalItems={1}
    />,
  );

  expect(screen.getByRole("spinbutton", { name: /current page/i })).toHaveValue(currentPage);
});

it("disables numeric input and buttons when data is loading", () => {
  render(
    <TablePagination
      currentPage={1}
      isLoading={true}
      itemsPerPage={10}
      onNextClick={() => {}}
      onPreviousClick={() => {}}
      setCurrentPage={() => {}}
      totalItems={1}
    />,
  );

  expect(screen.getByRole("spinbutton", { name: /current page/i })).toBeDisabled();
  expect(screen.getByRole("button", { name: /previous page/i })).toBeDisabled();
  expect(screen.getByRole("button", { name: /next page/i })).toBeDisabled();
});
