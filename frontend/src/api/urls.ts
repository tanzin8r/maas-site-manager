import { getApiUrl } from "./utils";

const urls = {
  sites: getApiUrl("/sites"),
  tokens: getApiUrl("/tokens"),
  enrollmentRequests: getApiUrl("/requests"),
};

export default urls;
