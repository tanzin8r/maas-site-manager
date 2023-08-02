import { useState } from "react";

import type { SitesSortKey, SortBy } from "@/api/handlers";
import Map from "@/components/Map";
import SitesHiddenButton from "@/components/Map/SitesHiddenButton/SitesHiddenButton";
import SitesTableControls from "@/components/SitesList/SitesTable/SitesTableControls/SitesTableControls";
import { useSitesQuery } from "@/hooks/react-query";
import useDebounce from "@/hooks/useDebouncedValue";
import { formatSiteMarker, parseSearchTextToQueryParams } from "@/utils";

const RegionsMap = () => {
  const [searchText, setSearchText] = useState("");
  const debounceSearchText = useDebounce(searchText);

  // TODO: https://warthogs.atlassian.net/browse/MAASENG-1990
  const { data, isLoading } = useSitesQuery(
    // this is temporary until we have the sites list endpoint for the map
    {
      page: "1",
      size: "50",
      sort_by: "name" as SortBy<SitesSortKey>,
    },
    parseSearchTextToQueryParams(debounceSearchText),
  );

  return (
    <div className="regions-map">
      <div className="regions-map__controls-wrapper">
        <SitesTableControls data={data} isLoading={isLoading} setSearchText={setSearchText} />
      </div>
      <section aria-label="regions map">
        <Map markers={data?.items.map(formatSiteMarker) ?? null} />
      </section>
      <SitesHiddenButton />
    </div>
  );
};

export default RegionsMap;
