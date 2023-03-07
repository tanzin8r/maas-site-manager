import { useQuery } from "@tanstack/react-query";

import type { GetSitesQueryParams } from "../api/handlers";
import { getSites } from "../api/handlers";
import type { SitesQueryResult } from "../api/types";

export type UseSitesQueryResult = ReturnType<typeof useSitesQuery>;

export const useSitesQuery = ({ page, size }: GetSitesQueryParams) =>
  useQuery<SitesQueryResult>({
    queryKey: ["sites", page, size],
    queryFn: () => getSites({ page, size }),
    keepPreviousData: true,
  });
