import type { Coordinates } from "@/apiclient";

export type CoordinatesFormValue = `${Coordinates["latitude"]}, ${Coordinates["longitude"]}` | "";
