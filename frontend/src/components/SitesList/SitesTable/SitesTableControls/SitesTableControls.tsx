import { SearchBox } from "@canonical/react-components";
import classNames from "classnames";

import ColumnsVisibilityControl from "./ColumnsVisibilityControl";
import SitesCount from "./SitesCount";
import SitesViewControl from "./SitesViewControl";

import type { SitesColumn } from "@/components/SitesList/SitesTable/SitesTable";
import RemoveButton from "@/components/base/RemoveButton";
import { useAppLayoutContext } from "@/context/AppLayoutContext";
import { useRowSelectionContext } from "@/context/RowSelectionContext";
import type { UseSitesQueryResult } from "@/hooks/react-query";
import { useLocation } from "@/utils/router";

const SitesTableControls = ({
  totalSites,
  isLoading,
  allColumns,
  setSearchText,
}: { allColumns?: SitesColumn[]; setSearchText: (text: string) => void; totalSites: number | null } & Pick<
  UseSitesQueryResult,
  "isLoading"
>) => {
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
          />
        </div>
        <div className="u-flex u-flex--column u-flex--row-small u-flex u-flex--justify-end">
          <RemoveButton
            disabled={isRemoveDisabled}
            onClick={() => setSidebar("removeRegions")}
            showDeleteIcon
            type="button"
          />
          {allColumns && <ColumnsVisibilityControl columns={allColumns} />}
          <SitesViewControl />
        </div>
      </div>
    </div>
  );
};

export default SitesTableControls;
