import { baseURL } from "@/api/config";

export const getApiUrl = (path: string): string => {
  return `${baseURL}/api/v1${path}`;
};

export const apiUrls = {
  login: getApiUrl("/login"),
  logout: getApiUrl("/logout"),
  sites: getApiUrl("/sites"),
  sitesCoordinates: getApiUrl("/sites/coordinates"),
  tokens: getApiUrl("/tokens"),
  tokensExport: getApiUrl("/tokens/export"),
  users: getApiUrl("/users"),
  enrollmentRequests: getApiUrl("/requests"),
  currentUser: getApiUrl("/users/me"),
};
