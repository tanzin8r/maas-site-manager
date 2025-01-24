import type { CoordinatesFormValue } from "./types";

import type { Coordinates } from "@/api";

export const parseCoordinatesFormValue = (value: CoordinatesFormValue): Coordinates => {
  const coordinatesValues = value
    .replace(/\s+/g, "")
    .split(",")
    .map((coordinate) => Number(coordinate));
  return {
    latitude: coordinatesValues[0],
    longitude: coordinatesValues[1],
  };
};
