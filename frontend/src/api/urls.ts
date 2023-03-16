import { getApiUrl } from "./utils";

const urls = {
  sites: getApiUrl("/sites"),
  tokens: getApiUrl("/tokens"),
};

export default urls;
