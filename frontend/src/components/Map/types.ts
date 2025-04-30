import type { Site } from "@/apiclient";

export type SiteMarkerType = Pick<Site, "id"> & {
  // Longitude, latitude https://datatracker.ietf.org/doc/html/rfc7946#section-3.1.1
  position: [number, number];
};

export type MapProps = {
  markers: SiteMarkerType[] | null;
  onBoundsChange?: (bounds: string) => void;
};
