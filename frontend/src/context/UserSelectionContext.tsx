import { getSelectedEntityContext, getSelectedEntityContextProvider, useSelectedEntityContext } from "./utils";

import type { User } from "@/apiclient";

export const UserSelectionContextProvider = getSelectedEntityContextProvider<User["id"]>("userSelection");
export const UserSelectionContext = getSelectedEntityContext<User["id"]>("userSelection");
export const useUserSelectionContext = () => useSelectedEntityContext<User["id"]>("userSelection");
export type UserSelectionContextValue = ReturnType<typeof useUserSelectionContext>;
