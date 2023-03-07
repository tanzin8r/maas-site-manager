import countries, { getName } from "i18n-iso-countries";
import en from "i18n-iso-countries/langs/en.json";

if (typeof window !== "undefined") {
  countries.registerLocale(en);
}

export const getCountryName = (countryCode: string) => {
  return getName(countryCode, "en", { select: "official" });
};
