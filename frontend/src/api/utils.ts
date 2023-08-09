import { baseURL } from "./config";

export const getApiUrl = (path: string) => {
  return baseURL + path;
};
