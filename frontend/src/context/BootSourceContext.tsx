import { getSelectedEntityContext, getSelectedEntityContextProvider, useSelectedEntityContext } from "./utils";

import type { BootSource } from "@/apiclient";

export const BootSourceContextProvider = getSelectedEntityContextProvider<BootSource["id"]>("bootSource");
export const BootSourceContext = getSelectedEntityContext<BootSource["id"]>("bootSource");
export const useBootSourceContext = () => useSelectedEntityContext<BootSource["id"]>("bootSource");
export type BootSourceContextValue = ReturnType<typeof useBootSourceContext>;
