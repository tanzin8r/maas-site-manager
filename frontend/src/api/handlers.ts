import api from "./api";
import urls from "./urls";

export type GetSitesQueryParams = {
  page: string;
  size: string;
};

export const getSites = async (params: GetSitesQueryParams) => {
  try {
    const response = await api.get(urls.sites, { params });
    return response.data;
  } catch (error) {
    // eslint-disable-next-line no-console
    console.error(error);
  }
};
