import { createContext } from "react";

import type { Site } from "@/api/types";

export type RegionDetailsId = Site["id"] | null;

export const RegionDetailsContext = createContext<{
  regionId: RegionDetailsId;
  setRegionId: (regionId: RegionDetailsId) => void;
}>({
  regionId: null,
  setRegionId: () => null,
});

export const RegionDetailsContextProvider = ({ children }: { children: React.ReactNode }) => {
  const [regionId, setRegionId] = useState<RegionDetailsId>(null);

  return <RegionDetailsContext.Provider value={{ regionId, setRegionId }}>{children}</RegionDetailsContext.Provider>;
};

export const useRegionDetailsContext = () => useContext(RegionDetailsContext);
