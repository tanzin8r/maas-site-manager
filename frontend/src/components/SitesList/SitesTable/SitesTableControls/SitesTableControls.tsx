import { SearchBox } from "@canonical/react-components";
import classNames from "classnames";

import SitesCount from "./SitesCount";
import SitesViewControl from "./SitesViewControl";

import RemoveButton from "@/components/base/RemoveButton";
import { useAppLayoutContext } from "@/context/AppLayoutContext";
import { useRowSelectionContext } from "@/context/RowSelectionContext";
import type { UseSitesQueryResult } from "@/hooks/react-query";
import { useLocation } from "@/utils/router";

const SitesTableControls = ({
  totalSites,
  isLoading,
  setSearchText,
  searchText,
}: {
  setSearchText: (text: string) => void;
  totalSites: number | null;
  searchText: string;
} & Pick<UseSitesQueryResult, "isLoading">) => {
  const handleSearchInput = (inputValue: string) => {
    setSearchText(inputValue);
  };
  const { pathname } = useLocation();
  const { setSidebar } = useAppLayoutContext();
  const { rowSelection } = useRowSelectionContext("sites");
  const isRemoveDisabled = Object.keys(rowSelection).length <= 0;
  const isMapView = pathname === "/sites/map";

  return (
    <div className={classNames("u-fixed-width sites-table-controls", { "is-map-view": isMapView })}>
      <div className="u-flex--large">
        <div>
          <h2 className="p-heading--4 u-no-padding--top site-control-heading">
            <SitesCount isLoading={isLoading} totalSites={totalSites} />
          </h2>
        </div>
        <div className="u-flex--grow">
          <SearchBox
            className="sites-table-controls__search"
            externallyControlled
            onChange={handleSearchInput}
            placeholder="Search and filter"
            value={searchText}
          />
        </div>
        <div className="u-flex u-flex--column u-flex--row-small u-flex u-flex--justify-end">
          <RemoveButton
            disabled={isRemoveDisabled}
            onClick={() => setSidebar("removeSites")}
            showDeleteIcon
            type="button"
          />
          <SitesViewControl />
        </div>
      </div>
    </div>
  );
};

export default SitesTableControls;
