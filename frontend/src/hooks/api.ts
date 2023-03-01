import { useQuery } from "react-query";

import { getSites } from "../api/handlers";
import type { SitesQueryResult } from "../api/types";

export const useSitesQuery = () => useQuery<SitesQueryResult>("/api/sites", getSites);
export type UseSitesQueryResult = ReturnType<typeof useSitesQuery>;
