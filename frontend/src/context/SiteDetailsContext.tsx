import { getSelectedEntityContext, getSelectedEntityContextProvider, useSelectedEntityContext } from "./utils";

import type { Site } from "@/api/types";

export const SiteDetailsContextProvider = getSelectedEntityContextProvider<Site["id"]>("siteDetails");
export const SiteDetailsContext = getSelectedEntityContext<Site["id"]>("siteDetails");
export const useSiteDetailsContext = () => useSelectedEntityContext<Site["id"]>("siteDetails");
export type SiteDetailsContextValue = ReturnType<typeof useSiteDetailsContext>;
