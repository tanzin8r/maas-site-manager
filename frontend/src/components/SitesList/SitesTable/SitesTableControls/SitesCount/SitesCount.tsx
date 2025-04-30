import pluralize from "pluralize";

import type { UseSitesResult } from "@/api/query/sites";
import Placeholder from "@/components/Placeholder";

const SitesCount = ({
  totalSites,
  isPending,
}: {
  totalSites: number | null;
} & Pick<UseSitesResult, "isPending">) =>
  isPending ? (
    <Placeholder isPending={isPending} text="xx" />
  ) : (
    <span>{`${pluralize("MAAS sites", totalSites || 0, !!totalSites)}`}</span>
  );

export default SitesCount;
