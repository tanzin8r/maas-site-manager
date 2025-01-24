import type { CoordinatesFormValue } from "./types";

import type { Coordinates } from "@/api";

/**
 * Converts a string containing coordinates into an object with latitude and longitude.
 * @param value A string containing coordinates.
 * @returns An object with latitude and longitude number properties
 */
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
