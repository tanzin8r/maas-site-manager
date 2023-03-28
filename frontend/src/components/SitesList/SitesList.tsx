import { useEffect, useState } from "react";

import { Pagination } from "@canonical/react-components";

import SitesTable from "./SitesTable";

import { useSitesQuery } from "@/hooks/api";
import useDebounce from "@/hooks/useDebouncedValue";
import { parseSearchTextToQueryParams } from "@/utils";

const DEFAULT_PAGE_SIZE = 50;

const SitesList = () => {
  const [page, setPage] = useState(0);
  const [size] = useState(DEFAULT_PAGE_SIZE);
  const [searchText, setSearchText] = useState("");
  const debounceSearchText = useDebounce(searchText);

  const { data, isLoading, isFetchedAfterMount } = useSitesQuery(
    { page: `${page}`, size: `${size}` },
    parseSearchTextToQueryParams(debounceSearchText),
  );

  useEffect(() => {
    setPage(0);
  }, [searchText]);

  return (
    <div>
      <SitesTable
        data={data}
        isFetchedAfterMount={isFetchedAfterMount}
        isLoading={isLoading}
        setSearchText={setSearchText}
      />
      <Pagination
        currentPage={page + 1}
        disabled={isLoading}
        itemsPerPage={size}
        paginate={(page) => {
          setPage(page - 1);
        }}
        totalItems={data?.total || 0}
      />
    </div>
  );
};

export default SitesList;
