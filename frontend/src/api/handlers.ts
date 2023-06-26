import api from "./api";
import type { Token } from "./types";
import urls from "./urls";

import { customParamSerializer } from "@/utils";

export type PostLoginData = {
  username: string;
  password: string;
};

export const postLogin = async (data: PostLoginData) => {
  if (!data?.username || !data?.password) {
    throw Error("Missing required fields");
  }
  try {
    const response = await api.post(urls.login, data);
    return response.data;
  } catch (error) {
    throw error;
  }
};

export type PostRegisterData = {
  username: string;
  password: string;
};

export type PaginationParams = {
  page: string;
  size: string;
};

export type SortKey = "name";
export type SortDirection = "asc" | "desc";
export type SortBy = `${SortKey}-${SortDirection}` | null;
export type SortingParams = {
  sort_by: SortBy;
};

export type GetSitesQueryParams = PaginationParams & SortingParams & {};
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
    throw error;
  }
};

export type PostTokensData = {
  amount: number;
  name?: string;
  duration: string; // <ISO 8601 duration string>,
};
export const postTokens = async (data: PostTokensData) => {
  if (!data?.amount || !data?.duration) {
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
    throw error;
  }
};

export const deleteTokens = async (data: Token["id"][]) => {
  if (data.length === 0) {
    throw Error("No tokens selected");
  }
  try {
    await api.delete(urls.tokens, { data });
  } catch (error) {
    throw error;
  }
};

export type GetEnrollmentRequestsQueryParams = PaginationParams & {};
export const getEnrollmentRequests = async (params: GetEnrollmentRequestsQueryParams) => {
  try {
    const response = await api.get(urls.enrollmentRequests, { params });
    return response.data;
  } catch (error) {
    throw error;
  }
};

export type PostEnrollmentRequestsData = {
  ids: string[];
  accept: boolean;
};
export const postEnrollmentRequests = async (data: PostEnrollmentRequestsData) => {
  if (!data?.ids || typeof data?.accept !== "boolean") {
    throw Error("Missing required fields");
  }
  try {
    const response = await api.post(urls.enrollmentRequests, data);
    return response.data;
  } catch (error) {
    throw error;
  }
};
