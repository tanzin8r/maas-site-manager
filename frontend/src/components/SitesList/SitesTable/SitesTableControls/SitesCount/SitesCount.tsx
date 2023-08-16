import pluralize from "pluralize";

import Placeholder from "@/components/Placeholder";
import type { UseSitesQueryResult } from "@/hooks/react-query";

const SitesCount = ({
  totalSites,
  isLoading,
}: {
  totalSites: number | null;
} & Pick<UseSitesQueryResult, "isLoading">) =>
  isLoading ? (
    <Placeholder isLoading={isLoading} text="xx" />
  ) : (
    <span>{`${pluralize("MAAS sites", totalSites || 0, !!totalSites)}`}</span>
  );

export default SitesCount;
