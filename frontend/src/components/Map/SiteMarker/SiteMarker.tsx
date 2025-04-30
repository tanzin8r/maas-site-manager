import classNames from "classnames";

import type { Site } from "@/apiclient";
import { createElementFromHTML, renderToHtmlString } from "@/components/Map/utils";

export type MarkerAppearance = "base" | "selected";

export const SiteMarkerSvg = ({ appearance = "base", id }: { appearance?: MarkerAppearance; id: Site["id"] }) => {
  return (
    <svg
      aria-label="site location marker"
      className={classNames("site-marker", { "is-selected": appearance === "selected" })}
      fill="none"
      height="47"
      id={`site-marker-${id}`}
      role="button"
      tabIndex={0}
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

const getMarkerHtml = (appearance: MarkerAppearance, id: Site["id"]): string =>
  renderToHtmlString(<SiteMarkerSvg appearance={appearance} id={id} />);

export const getSiteMarker = (appearance: MarkerAppearance, id: Site["id"]) => {
  return createElementFromHTML(getMarkerHtml(appearance, id));
};

export const getClusterSvg = (appearance: MarkerAppearance, count: number) =>
  `<svg tabindex="0" fill="none" role="button" aria-label="${count} sites cluster" viewBox="0 0 32 32" width="100%" height="100%" xmlns="http://www.w3.org/2000/svg">
    <rect
      class=${classNames("site-marker-cluster__body", { "has-selected": appearance === "selected" })}
      fill="#E95420"
      height="31"
      rx="28.5"
      width="31"
      x="0.5"
      y="0.5"
    />
  </svg>
  <span class="site-marker-cluster__text">${count}</span>`;

export const getClusterSize = (count: number, maxCount: number) => {
  const sizeModifiers = [
    { countLimit: 0.4 * maxCount, size: 32 },
    { countLimit: 0.6 * maxCount, size: 48 },
    { countLimit: 0.8 * maxCount, size: 58 },
    { countLimit: Infinity, size: 88 },
  ] as const;
  const size = sizeModifiers.find(({ countLimit }) => count <= countLimit)!.size;
  return size;
};

export const createCustomClusterIcon = function (appearance: MarkerAppearance, count: number, maxCount = 100) {
  const iconSize = getClusterSize(count, maxCount);
  const svg = getClusterSvg(appearance, count);

  return createElementFromHTML(
    `<div class="site-marker-cluster" style="width: ${iconSize}px; height: ${iconSize}px;">${svg}</div>`,
  );
};
