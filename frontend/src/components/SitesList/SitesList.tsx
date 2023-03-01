import { useSitesQuery } from "../../hooks/api";

import SitesTable from "./components/SitesTable";

const SitesList = () => {
  const { data, isLoading, isFetchedAfterMount } = useSitesQuery();

  return (
    <div>
      <SitesTable data={data} isFetchedAfterMount={isFetchedAfterMount} isLoading={isLoading} />
    </div>
  );
};

export default SitesList;
