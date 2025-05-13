import { baseURL } from "@/api/config";

export const getApiUrl = (path: string): string => {
  return `${baseURL}/v1${path}`;
};

export const apiUrls = {
  login: getApiUrl("/login"),
  logout: getApiUrl("/logout"),
  sites: getApiUrl("/sites"),
  sitesCoordinates: getApiUrl("/sites/coordinates"),
  tokens: getApiUrl("/tokens"),
  tokensExport: getApiUrl("/tokens/export"),
  users: getApiUrl("/users"),
  enrollmentRequests: getApiUrl("/sites/pending"),
  currentUser: getApiUrl("/users/me"),
  imageSources: getApiUrl("/bootasset-sources"),
  bootAssets: getApiUrl("/bootassets"),
  images: getApiUrl("/images"),
  upstreamImages: getApiUrl("/images/upstream"),
  upstreamImageSource: getApiUrl("/images/upstream-source"),
  settings: getApiUrl("/settings"),
};
