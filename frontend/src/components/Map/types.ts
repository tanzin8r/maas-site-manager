import type { LatLngExpression } from "leaflet";

import type { Site } from "@/api/types";

export type SiteMarkerType = Pick<Site, "id" | "name"> & {
  position: LatLngExpression;
};
