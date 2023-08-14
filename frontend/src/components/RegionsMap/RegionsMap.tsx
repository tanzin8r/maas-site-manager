import { useState, useEffect } from "react";

import Map from "@/components/Map";
import SitesHiddenButton from "@/components/Map/SitesHiddenButton/SitesHiddenButton";
import SitesTableControls from "@/components/SitesList/SitesTable/SitesTableControls/SitesTableControls";
import { useSitesCoordinatesQuery } from "@/hooks/react-query";
import useDebounce from "@/hooks/useDebouncedValue";
import { formatSiteMarker, parseSearchTextToQueryParams } from "@/utils";
import { useNavigate, useSearchParams } from "@/utils/router";

const RegionsMap = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [isFirstVisit, setIsFirstVisit] = useState(true);
  const [searchText, setSearchText] = useState(searchParams.get("q") || "");
  const debounceSearchText = useDebounce(searchText);

  const { data, isLoading } = useSitesCoordinatesQuery(parseSearchTextToQueryParams(debounceSearchText));

  useEffect(() => {
    if (isFirstVisit) {
      setIsFirstVisit(false);
      return;
    }

    if (!debounceSearchText) {
      navigate("/sites/map");
      return;
    }
    const params = { q: debounceSearchText };
    const urlParams = new URLSearchParams(params);
    navigate({ pathname: "/sites/map", search: urlParams.toString() });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [debounceSearchText, navigate]);

  return (
    <div className="regions-map">
      <div className="regions-map__controls-wrapper">
        <SitesTableControls
          isLoading={isLoading}
          searchText={searchText}
          setSearchText={setSearchText}
          totalSites={data?.length ?? null}
        />
      </div>
      <section aria-label="regions map">
        <Map markers={data?.map?.(formatSiteMarker) ?? null} />
      </section>
      <SitesHiddenButton />
    </div>
  );
};

export default RegionsMap;
