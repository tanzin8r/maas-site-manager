import { useState, useEffect } from "react";

import { ContentSection } from "@canonical/maas-react-components";

import Map from "@/components/Map";
import SitesHiddenButton from "@/components/Map/SitesHiddenButton/SitesHiddenButton";
import SitesTableControls from "@/components/SitesList/SitesTable/SitesTableControls/SitesTableControls";
import { useSitesCoordinatesQuery } from "@/hooks/react-query";
import useDebounce from "@/hooks/useDebouncedValue";
import { formatSiteMarker, parseSearchTextToQueryParams } from "@/utils";
import { useNavigate, useSearchParams } from "@/utils/router";

const SitesMap = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [isFirstVisit, setIsFirstVisit] = useState(true);
  const [searchText, setSearchText] = useState(searchParams.get("q") || "");
  const debounceSearchText = useDebounce(searchText);

  const { data, isPending } = useSitesCoordinatesQuery(parseSearchTextToQueryParams(debounceSearchText));

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
    <ContentSection className="sites-map">
      <ContentSection.Header className="sites-map__controls-wrapper">
        <SitesTableControls
          isPending={isPending}
          searchText={searchText}
          setSearchText={setSearchText}
          totalSites={data?.length ?? null}
        />
      </ContentSection.Header>
      <section aria-label="sites map">
        <Map markers={data?.map?.(formatSiteMarker) ?? null} />
      </section>
      {data?.some((site) => site.coordinates === null) ? <SitesHiddenButton /> : null}
    </ContentSection>
  );
};

export default SitesMap;
