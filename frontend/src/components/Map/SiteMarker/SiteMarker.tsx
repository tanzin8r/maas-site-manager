import classNames from "classnames";
import L from "leaflet";
import { flushSync } from "react-dom";
import { createRoot } from "react-dom/client";
import { Marker, Popup } from "react-leaflet";

import RegionSummary from "@/components/Map/RegionSummary/RegionSummary";
import type { SiteMarkerType } from "@/components/Map/types";

type MarkerApprearance = "base" | "selected";
const SiteMarkerSvg = ({ appearance = "base" }: { appearance?: MarkerApprearance }) => {
  return (
    <svg
      className={classNames("site-marker", { "is-selected": appearance === "selected" })}
      fill="none"
      height="47"
      viewBox="0 0 29 47"
      width="29"
      xmlns="http://www.w3.org/2000/svg"
    >
      <path
        className="site-marker__body"
        d="M2.30193 19.662L2.30196 19.662L13.8721 44.2132L14.3244 45.1729L14.7767 44.2131L26.3453 19.662C30.4493 10.9537 24.3354 0.748358 14.693 0.504555L14.6927 0.504548C14.5699 0.501516 14.4471 0.5 14.3244 0.5C14.2016 0.5 14.0788 0.501516 13.956 0.504548L13.9557 0.504555C4.31178 0.748358 -1.80055 10.9537 2.30193 19.662Z"
      />
      <path
        className="site-marker__circle"
        d="M14.3233 19.9004C17.1553 19.9004 19.4512 17.6046 19.4512 14.7725C19.4512 11.9404 17.1553 9.64453 14.3233 9.64453C11.4912 9.64453 9.19531 11.9404 9.19531 14.7725C9.19531 17.6046 11.4912 19.9004 14.3233 19.9004Z"
      />
    </svg>
  );
};

const getMarkerHtml = (appearance: MarkerApprearance): string => {
  const div = document.createElement("div");
  const root = createRoot(div);

  flushSync(() => {
    root.render(<SiteMarkerSvg appearance={appearance} />);
  });

  return div.innerHTML;
};

const createDivIcon = (appearance: MarkerApprearance) => {
  return new L.DivIcon({
    html: markerHtml[appearance],
    iconAnchor: [14.5, 47],
    iconSize: [29, 47],
  });
};

const markerHtml = {
  base: getMarkerHtml("base"),
  selected: getMarkerHtml("selected"),
} as const;

const markerIcon = {
  base: createDivIcon("base"),
  selected: createDivIcon("selected"),
};

export const BaseMarker = markerIcon.base;
export const SelectedMarker = markerIcon.selected;

export const getSiteMarker = (appearance: keyof typeof markerIcon) => {
  return markerIcon[appearance];
};

const SiteMarker = ({ name, id, position }: SiteMarkerType) => {
  const eventHandlers = useMemo(
    () => ({
      mouseover() {},
      mouseout() {},
      dragend() {},
      click() {},
    }),
    [],
  );

  return (
    <Marker alt={name} eventHandlers={eventHandlers} icon={getSiteMarker("base")} keyboard position={position}>
      <Popup minWidth={300}>
        <RegionSummary id={id} />
      </Popup>
    </Marker>
  );
};

export default SiteMarker;
