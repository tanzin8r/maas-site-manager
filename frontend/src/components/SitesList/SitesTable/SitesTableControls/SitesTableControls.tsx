import { Row, Col, SearchBox, Button, Icon } from "@canonical/react-components";

import ColumnsVisibilityControl from "./ColumnsVisibilityControl";
import SitesCount from "./SitesCount";

import type { SitesColumn } from "@/components/SitesList/SitesTable/SitesTable";
import { useAppContext } from "@/context";
import type { UseSitesQueryResult } from "@/hooks/api";

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
  const { rowSelection, setSidebar } = useAppContext();
  const isRemoveDisabled = Object.keys(rowSelection).length <= 0;

  return (
    <Row>
      <Col size={2}>
        <h2 className="p-heading--4">
          <SitesCount data={data} isLoading={isLoading} />
        </h2>
      </Col>
      <Col size={6}>
        <SearchBox externallyControlled onChange={handleSearchInput} placeholder="Search and filter" />
      </Col>
      <Col className="u-flex u-flex--align-end u-flex--column" size={2}>
        <Button
          appearance="negative"
          disabled={isRemoveDisabled}
          onClick={() => setSidebar("removeRegions")}
          type="button"
        >
          <Icon light name="delete" /> Remove
        </Button>
      </Col>
      <Col className="u-flex u-flex--align-end u-flex--column" size={2}>
        <ColumnsVisibilityControl columns={allColumns} />
      </Col>
    </Row>
  );
};

export default SitesTableControls;
