import { SearchBox, Button, Icon } from "@canonical/react-components";

import ColumnsVisibilityControl from "./ColumnsVisibilityControl";
import SitesCount from "./SitesCount";

import type { SitesColumn } from "@/components/SitesList/SitesTable/SitesTable";
import { useAppContext } from "@/context/AppContext";
import { useRowSelectionContext } from "@/context/RowSelectionContext";
import type { UseSitesQueryResult } from "@/hooks/react-query";

const SitesTableControls = ({
  data,
  isLoading,
  allColumns,
  setSearchText,
}: { allColumns: SitesColumn[]; setSearchText: (text: string) => void } & Pick<
  UseSitesQueryResult,
  "data" | "isLoading"
>) => {
  const handleSearchInput = (inputValue: string) => {
    setSearchText(inputValue);
  };
  const { setSidebar } = useAppContext();
  const { rowSelection } = useRowSelectionContext("sites");
  const isRemoveDisabled = Object.keys(rowSelection).length <= 0;

  return (
    <div className="u-fixed-width sites-table-controls">
      <div className="u-flex--large">
        <div>
          <h2 className="p-heading--4">
            <SitesCount data={data} isLoading={isLoading} />
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
        <div className="u-flex u-flex--justify-end">
          <Button
            appearance="negative"
            disabled={isRemoveDisabled}
            onClick={() => setSidebar("removeRegions")}
            type="button"
          >
            <Icon light name="delete" /> Remove
          </Button>
          <ColumnsVisibilityControl columns={allColumns} />
        </div>
      </div>
    </div>
  );
};

export default SitesTableControls;
