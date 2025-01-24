import type { Coordinates } from "@/api/client";

export type CoordinatesFormValue = `${Coordinates["latitude"]}, ${Coordinates["longitude"]}` | "";
