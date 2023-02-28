import { useSitesQuery } from "../../hooks/api";

import SitesTable from "./components/SitesTable";

const SitesList = () => {
  const query = useSitesQuery();

  return (
    <div>
      <h2 className="p-heading--4">{query?.data?.items?.length || ""} MAAS Regions</h2>
      {query.isLoading && !query.isFetchedAfterMount ? "Loading..." : null}
      {query.isFetchedAfterMount && query.data ? <SitesTable data={query.data.items} /> : null}
    </div>
  );
};

export default SitesList;
