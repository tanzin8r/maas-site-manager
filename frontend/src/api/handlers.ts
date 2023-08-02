import api from "./api";
import type { Token, User } from "./types";
import urls from "./urls";

import type { RegionDetailsId } from "@/context/RegionDetailsContext";
import { customParamSerializer, customParamWithSearchTextSerializer } from "@/utils";

export type PostLoginData = {
  email: string;
  password: string;
};

export const postLogin = async (data: PostLoginData) => {
  if (!data?.email || !data?.password) {
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

export type SortDirection = "asc" | "desc";

export type SitesSortKey = "name";
export type UserSortKey = "username" | "full_name" | "email";

export type SortBy<T extends SitesSortKey | UserSortKey> = `${T}-${SortDirection}` | null;
export type SortingParams<T extends SitesSortKey | UserSortKey> = {
  sort_by: SortBy<T>;
};

export type GetSitesQueryParams = PaginationParams & SortingParams<SitesSortKey> & {};
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

export const getSite = async (id: RegionDetailsId) => {
  try {
    const response = await api.get(`${urls.sites}/${id}`);
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

export type GetUsersQueryParams = PaginationParams & SortingParams<UserSortKey> & {};
export const getUsers = async (params: GetUsersQueryParams, searchText?: string) => {
  try {
    const response = await api.get(urls.users, {
      params,
      paramsSerializer: { serialize: (params) => customParamWithSearchTextSerializer(params, searchText) },
    });
    return response.data;
  } catch (error) {
    throw error;
  }
};

export const getUser = async (id: User["id"]) => {
  try {
    const response = await api.get(`${urls.users}/${id}`);
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

export const getCurrentUser = async () => {
  try {
    const response = await api.get(urls.currentUser);
    return response.data;
  } catch (error) {
    throw error;
  }
};

export type UserUpdateData = Omit<User, "id"> & { password: string; confirm_password: string };

export type UpdateUserPayload = {
  userId: number;
  userData: Partial<UserUpdateData>;
};

export const updateUser = async (data: UpdateUserPayload) => {
  try {
    const response = await api.patch(`${urls.users}/${data.userId}`, data.userData);
    return response.data;
  } catch (error) {
    throw error;
  }
};

export const addUser = async (data: Omit<User, "id">) => {
  try {
    const response = await api.post(urls.users, data);
    return response.data;
  } catch (error) {
    throw error;
  }
};

export const deleteUser = async (userId: number) => {
  try {
    await api.delete(`${urls.users}/${userId}`);
  } catch (error) {
    throw error;
  }
};
