import { createContext, useContext, useState } from "react";

export type Sidebar =
  | "removeRegions"
  | "createToken"
  | "addUser"
  | "editUser"
  | "deleteUser"
  | "regionDetails"
  | "editRegion"
  | null;
export const AppLayoutContext = createContext<{
  sidebar: Sidebar;
  setSidebar: (sidebar: Sidebar) => void;
}>({
  sidebar: null,
  setSidebar: () => null,
});

export const AppLayoutContextProvider = ({ children }: { children: React.ReactNode }) => {
  const [sidebar, setSidebar] = useState<Sidebar>(null);

  return <AppLayoutContext.Provider value={{ sidebar, setSidebar }}>{children}</AppLayoutContext.Provider>;
};

export const useAppLayoutContext = () => useContext(AppLayoutContext);
