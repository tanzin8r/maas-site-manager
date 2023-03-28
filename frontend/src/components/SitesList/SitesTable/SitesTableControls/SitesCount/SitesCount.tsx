import pluralize from "pluralize";

import Placeholder from "@/components/Placeholder";
import type { UseSitesQueryResult } from "@/hooks/api";

const SitesCount = ({ data, isLoading }: Pick<UseSitesQueryResult, "data" | "isLoading">) =>
  isLoading ? (
    <Placeholder isLoading={isLoading} text="xx" />
  ) : (
    <span>{`${pluralize("MAAS regions", data?.total || 0, !!data?.total)}`}</span>
  );

export default SitesCount;
