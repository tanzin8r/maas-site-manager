import * as Yup from "yup";

export const coordinateSchema = Yup.string()
  .matches(
    /^(-?\d+(\.\d*)?),\s*(-?\d+(\.\d*)?)$/,
    "Latitude and Longitude input can only contain numerical characters (0-9), a decimal point (.), a comma (,), or a minus (-).",
  )
  .matches(
    /^[-]?([1-8]?\d(\.\d+)?|90(\.0+)?)\s*,\s*[-+]?(180(\.0+)?|((1[0-7]\d)|([1-9]?\d))(\.\d+)?)$/,
    "Invalid latitude and longitude. Please make sure the coordinates provided are valid and separated by a comma (,).",
  );
