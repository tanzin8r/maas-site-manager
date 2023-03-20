import api from "./api";
import urls from "./urls";

import { customParamSerializer } from "@/utils";

export type PaginationParams = {
  page: string;
  size: string;
};
export type GetSitesQueryParams = PaginationParams & {};

export const getSites = async (params: GetSitesQueryParams, queryText?: string) => {
  try {
    const response = await api.get(urls.sites, {
      params,
      paramsSerializer: {
        serialize: (params) => customParamSerializer(params, queryText),
      },
    });
    return response.data;
  } catch (error) {
    // eslint-disable-next-line no-console
    console.error(error);
  }
};

export type PostTokensData = {
  amount: number;
  name?: string;
  expires: string; // <ISO 8601 date string>,
};

export const postTokens = async (data: PostTokensData) => {
  if (!data?.amount || !data?.expires) {
    throw Error("Missing required fields");
  }
  try {
    const response = await api.post(urls.tokens, data);
    return response.data;
  } catch (error) {
    throw error;
  }
};

export type GetTokensQueryParams = PaginationParams & {};

export const getTokens = async (params: GetTokensQueryParams) => {
  try {
    const response = await api.get(urls.tokens, { params });
    return response.data;
  } catch (error) {
    // eslint-disable-next-line no-console
    console.error(error);
  }
};
