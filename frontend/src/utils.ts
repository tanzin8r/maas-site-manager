import * as Sentry from "@sentry/browser";
import { parseISO } from "date-fns";
import { getTimezoneOffset, format, utcToZonedTime } from "date-fns-tz";
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

export const getTimezoneUTCString = (timezone: string, date?: Date | number) => {
  const offset = getTimezoneOffset(timezone, date);
  const sign = offset < 0 ? "-" : "+";
  const absOffset = Math.abs(offset);
  const minutes = Math.floor(absOffset / 60000) % 60;
  const hours = Math.floor(absOffset / 60000 / 60);
  if (absOffset > 0) {
    return `${sign}${hours}` + (minutes > 0 ? `:${minutes}` : "");
  } else {
    return "";
  }
};

export const getTimeInTimezone = (date: Date, timezone: string) => {
  const time = date.getTime() + getTimezoneOffset(timezone);
  const hours = `${new Date(time).getUTCHours()}`.padStart(2, "0");
  const minutes = `${new Date(time).getUTCMinutes()}`.padStart(2, "0");
  return hours + ":" + minutes;
};

export const formatUTCDateString = (dateString: string) =>
  format(utcToZonedTime(parseISO(dateString), "UTC"), "yyyy-MM-dd HH:mm", { timeZone: "UTC" });

export const copyToClipboard = (text: string, callback?: (text: string) => void) => {
  navigator.clipboard
    .writeText(text)
    .then(() => {
      callback && callback(text);
    })
    .catch((error) => {
      Sentry.captureException(new Error("copy to clipboard failed", { cause: error }));
    });
};
