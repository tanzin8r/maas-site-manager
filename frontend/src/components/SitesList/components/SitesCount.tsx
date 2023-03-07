import pluralize from "pluralize";

import type { UseSitesQueryResult } from "../../../hooks/api";
import Placeholder from "../../Placeholder";

const SitesCount = ({ data, isLoading }: Pick<UseSitesQueryResult, "data" | "isLoading">) =>
  isLoading ? (
    <Placeholder isLoading={isLoading} text="xx" />
  ) : (
    <span>{`${pluralize("MAAS regions", data?.total || 0, !!data?.total)}`}</span>
  );

export default SitesCount;
