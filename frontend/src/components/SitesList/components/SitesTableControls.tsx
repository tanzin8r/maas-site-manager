import { useState } from "react";

import { Row, Col, SearchBox } from "@canonical/react-components";

import type { UseSitesQueryResult } from "../../../hooks/api";

import ColumnsVisibilityControl from "./ColumnsVisibilityControl";
import SitesCount from "./SitesCount";
import type { SitesColumn } from "./SitesTable";

const SitesTableControls = ({
  data,
  isLoading,
  allColumns,
}: { allColumns: SitesColumn[] } & Pick<UseSitesQueryResult, "data" | "isLoading">) => {
  const [searchText, setSearchText] = useState("");
  const handleSearchInput = (inputValue: string) => {
    setSearchText(inputValue);
  };

  return (
    <Row>
      <Col size={2}>
        <h2 className="p-heading--4">
          <SitesCount data={data} isLoading={isLoading} />
        </h2>
      </Col>
      <Col size={8}>
        <SearchBox
          externallyControlled
          onChange={handleSearchInput}
          placeholder="Search and filter"
          value={searchText}
        />
      </Col>
      <Col className="u-flex u-flex--align-end u-flex--column" size={2}>
        <ColumnsVisibilityControl columns={allColumns} />
      </Col>
    </Row>
  );
};

export default SitesTableControls;
