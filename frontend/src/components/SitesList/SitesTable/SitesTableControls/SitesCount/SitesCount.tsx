import pluralize from "pluralize";

import Placeholder from "@/components/Placeholder";
import type { UseSitesQueryResult } from "@/hooks/react-query";

const SitesCount = ({
  totalSites,
  isPending,
}: {
  totalSites: number | null;
} & Pick<UseSitesQueryResult, "isPending">) =>
  isPending ? (
    <Placeholder isPending={isPending} text="xx" />
  ) : (
    <span>{`${pluralize("MAAS sites", totalSites || 0, !!totalSites)}`}</span>
  );

export default SitesCount;
