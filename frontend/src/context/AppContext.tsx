import { createContext, useContext, useState } from "react";

export const AppContext = createContext<{
  sidebar: "removeRegions" | "createToken" | null;
  setSidebar: (sidebar: "removeRegions" | "createToken" | null) => void;
}>({
  sidebar: null,
  setSidebar: () => null,
});

export const AppContextProvider = ({ children }: { children: React.ReactNode }) => {
  const [sidebar, setSidebar] = useState<"removeRegions" | "createToken" | null>(null);

  return <AppContext.Provider value={{ sidebar, setSidebar }}>{children}</AppContext.Provider>;
};

export const useAppContext = () => useContext(AppContext);
