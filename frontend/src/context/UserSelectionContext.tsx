import { createContext, useContext, useState } from "react";

import type { User } from "@/api/types";

export type SelectedUserId = User["id"] | null | undefined;

export const UserSelectionContext = createContext<{
  selectedUserId: SelectedUserId;
  setSelectedUserId: (selectedUserId: SelectedUserId) => void;
}>({
  selectedUserId: null,
  setSelectedUserId: () => null,
});

export const UserSelectionContextProvider = ({ children }: { children: React.ReactNode }) => {
  const [selectedUserId, setSelectedUserId] = useState<SelectedUserId>(null);

  return (
    <UserSelectionContext.Provider value={{ selectedUserId, setSelectedUserId }}>
      {children}
    </UserSelectionContext.Provider>
  );
};

export const useUserSelectionContext = () => useContext(UserSelectionContext);
