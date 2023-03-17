import { getTimezoneOffset } from "date-fns-tz";
import * as countries from "i18n-iso-countries";
import { getName } from "i18n-iso-countries";
import en from "i18n-iso-countries/langs/en.json";

if (typeof window !== "undefined") {
  countries.registerLocale(en);
}

export const getCountryName = (countryCode: string) => {
  return getName(countryCode, "en", { select: "official" });
};

export const parseSearchTextToQueryParams = (text: string) => {
  // if text:result => text=result
  if (!text) return "";
  const parsedText = text
    .split(" ")
    .map((item) => (item.includes(":") ? item.replaceAll(":", "=") : ""))
    .join("&");
  if (parsedText.at(-1) === "&") {
    return parsedText.substring(0, parsedText.length - 1);
  }
  return parsedText;
};

export const customParamSerializer = (params: Record<string, string>, queryText?: string) => {
  return (
    Object.entries(Object.assign({}, params))
      .map(([key, value]) => `${key}=${value}`)
      .join("&") + `${queryText ? "&" + queryText : ""}`
  );
};

export const getTimezoneUTCString = (offset: number) => {
  const sign = offset < 0 ? "-" : "+";
  const absOffset = Math.abs(offset);
  const hours = Math.floor(absOffset);
  const minutes = Math.floor((absOffset - hours) * 60);
  const paddedHours = String(hours).padStart(2, "0");
  const paddedMinutes = String(minutes).padStart(2, "0");
  return sign + paddedHours + ":" + paddedMinutes;
};

export const getTimeByUTCOffset = (date: Date, offset: number) => {
  const utcString = getTimezoneUTCString(offset);
  const updatedTime = date.getTime() + getTimezoneOffset(utcString);
  const hours = `${new Date(updatedTime).getUTCHours()}`.padStart(2, "0");
  const minutes = `${new Date(updatedTime).getUTCMinutes()}`.padStart(2, "0");
  return hours + ":" + minutes;
};
