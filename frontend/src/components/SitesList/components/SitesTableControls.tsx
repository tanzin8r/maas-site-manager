import { Row, Col } from "@canonical/react-components";

import type { UseSitesQueryResult } from "../../../hooks/api";

import ColumnsVisibilityControl from "./ColumnsVisibilityControl";
import SitesCount from "./SitesCount";
import type { SitesColumn } from "./SitesTable";

const SitesTableControls = ({
  data,
  isLoading,
  allColumns,
}: { allColumns: SitesColumn[] } & Pick<UseSitesQueryResult, "data" | "isLoading">) => {
  return (
    <Row>
      <Col size={10}>
        <h2 className="p-heading--4">
          <SitesCount data={data} isLoading={isLoading} />
        </h2>
      </Col>
      <Col className="u-flex u-flex--align-end u-flex--column" size={2}>
        <ColumnsVisibilityControl columns={allColumns} />
      </Col>
    </Row>
  );
};

export default SitesTableControls;
