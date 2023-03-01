import { Row, Col } from "@canonical/react-components";

import type { UseSitesQueryResult } from "../../../hooks/api";
import Placeholder from "../../Placeholder";

import ColumnsVisibilityControl from "./ColumnsVisibilityControl";
import type { SitesColumn } from "./SitesTable";

const SitesCount = ({ data, isLoading }: Pick<UseSitesQueryResult, "data" | "isLoading">) =>
  isLoading ? <Placeholder isLoading={isLoading} text="xx" /> : <span>{`${data?.items?.length || ""}`}</span>;

const SitesTableControls = ({
  data,
  isLoading,
  allColumns,
}: { allColumns: SitesColumn[] } & Pick<UseSitesQueryResult, "data" | "isLoading">) => {
  return (
    <Row>
      <Col size={10}>
        <h2 className="p-heading--4">
          <SitesCount data={data} isLoading={isLoading} /> MAAS Regions
        </h2>
      </Col>
      <Col size={2}>
        <ColumnsVisibilityControl columns={allColumns} />
      </Col>
    </Row>
  );
};

export default SitesTableControls;
