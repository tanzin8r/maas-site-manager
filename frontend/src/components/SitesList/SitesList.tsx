import { useEffect, useState } from "react";

import type { SortingState } from "@tanstack/react-table";

import SitesTable from "./SitesTable";

import type { SortBy, SortKey } from "@/api/handlers";
import { useSitesQuery } from "@/hooks/react-query";
import useDebounce from "@/hooks/useDebouncedValue";
import usePagination from "@/hooks/usePagination";
import { parseSearchTextToQueryParams } from "@/utils";

const DEFAULT_PAGE_SIZE = 50;

const getSortBy = (sorting: SortingState): SortBy => {
  if (sorting.length !== 1) {
    return null;
  }
  const key = sorting[0].id as SortKey;
  return `${key}-${sorting[0].desc ? "desc" : "asc"}`;
};

const SitesList = () => {
  const [totalDataCount, setTotalDataCount] = useState(0);
  const { page, debouncedPage, size, handleNextClick, handlePreviousClick, handlePageSizeChange, setPage } =
    usePagination(DEFAULT_PAGE_SIZE, totalDataCount);
  const [searchText, setSearchText] = useState("");
  const debounceSearchText = useDebounce(searchText);
  const [sorting, setSorting] = useState<SortingState>([]);
  const sortBy = getSortBy(sorting);

  const { error, data, isLoading } = useSitesQuery(
    {
      page: `${debouncedPage}`,
      size: `${size}`,
      sort_by: sortBy,
    },
    parseSearchTextToQueryParams(debounceSearchText),
  );

  useEffect(() => {
    setPage(1);
  }, [searchText, setPage]);

  useEffect(() => {
    if (data && "total" in data) {
      setTotalDataCount(data.total);
    }
  }, [data]);

  return (
    <div>
      <SitesTable
        data={data}
        error={error}
        isLoading={isLoading}
        paginationProps={{
          currentPage: page,
          dataContext: "MAAS Regions",
          handlePageSizeChange,
          isLoading,
          itemsPerPage: size,
          onNextClick: handleNextClick,
          onPreviousClick: handlePreviousClick,
          setCurrentPage: setPage,
          totalItems: data?.total || 0,
        }}
        setSearchText={setSearchText}
        setSorting={setSorting}
        sorting={sorting}
      />
    </div>
  );
};

export default SitesList;
