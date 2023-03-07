import { useState } from "react";

import { Pagination } from "@canonical/react-components";

import { useSitesQuery } from "../../hooks/api";

import SitesTable from "./components/SitesTable";

const DEFAULT_PAGE_SIZE = 50;

const SitesList = () => {
  const [page, setPage] = useState(0);
  const [size] = useState(DEFAULT_PAGE_SIZE);
  const { data, isLoading, isFetchedAfterMount } = useSitesQuery({ page: `${page}`, size: `${size}` });

  return (
    <div>
      <SitesTable data={data} isFetchedAfterMount={isFetchedAfterMount} isLoading={isLoading} />
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
