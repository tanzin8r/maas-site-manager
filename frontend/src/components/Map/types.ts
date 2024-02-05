import type { Site } from "@/api/client";

export type SiteMarkerType = Pick<Site, "id"> & {
  // Latitute, longitude
  position: [number, number];
};

export type MapProps = {
  markers: SiteMarkerType[] | null;
  onBoundsChange?: (bounds: string) => void;
};
