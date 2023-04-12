import { getApiUrl } from "./utils";

const urls = {
  login: getApiUrl("/login"),
  logout: getApiUrl("/logout"),
  sites: getApiUrl("/sites"),
  tokens: getApiUrl("/tokens"),
  enrollmentRequests: getApiUrl("/requests"),
};

export default urls;
