import { apiClient } from "./api";
import type { Token, User } from "./types";

import type { LoginPostRequest, PendingSitesPostRequest, TokensPostRequest } from "@/api-client";

export type PostLoginData = {
  email: string;
  password: string;
};

export const postLogin = async (data: LoginPostRequest) => {
  if (!data?.email || !data?.password) {
    throw Error("Missing required fields");
  }
  try {
    const response = await apiClient.default.postApiV1LoginPost({ requestBody: data });
    return response;
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
  sortBy: SortBy<T>;
};

export type GetSitesQueryParams = PaginationParams & SortingParams<SitesSortKey> & {};

// TODO: integrate supported API params https://warthogs.atlassian.net/browse/MAASENG-2081
export const getSites = (params: Parameters<typeof apiClient.default.getApiV1SitesGet>[0]) =>
  apiClient.default.getApiV1SitesGet({
    page: Number(params.page),
    size: Number(params.size),
    sortBy: params.sortBy || null,
  });

// TODO: pass search params once API supports it https://warthogs.atlassian.net/browse/MAASENG-2080
export const getSitesCoordinates = async (_queryText?: string) =>
  apiClient.default.getCoordinatesApiV1SitesCoordinatesGet();

export const getSite = async ({ id }: Parameters<typeof apiClient.default.getIdApiV1SitesIdGet>[0]) => {
  const response = await apiClient.default.getIdApiV1SitesIdGet({ id });
  return response;
};

export const postTokens = async (data: TokensPostRequest) => {
  if (!data?.count || !data?.duration) {
    throw Error("Missing required fields");
  }
  try {
    const response = await apiClient.default.postApiV1TokensPost({ requestBody: data });
    return response;
  } catch (error) {
    throw error;
  }
};

export const getTokensExport = async () => {
  try {
    const response = await apiClient.default.getExportApiV1TokensExportGet();
    return response;
  } catch (error) {
    throw error;
  }
};

export type GetTokensQueryParams = PaginationParams & {};
export const getTokens = ({ page, size }: Parameters<typeof apiClient.default.getApiV1TokensGet>[0]) =>
  apiClient.default.getApiV1TokensGet({ page, size });

export const getUsers = async (params: Parameters<typeof apiClient.default.getApiV1UsersGet>[0]) => {
  try {
    const response = await apiClient.default.getApiV1UsersGet({
      ...params,
    });
    return response;
  } catch (error) {
    throw error;
  }
};

export const getUser = async ({ id }: Parameters<typeof apiClient.default.getIdApiV1UsersIdGet>[0]) => {
  const response = await apiClient.default.getIdApiV1UsersIdGet({ id });
  return response;
};

export const deleteTokens = async (data: Token["id"][]) => {
  if (data.length === 0) {
    throw Error("No tokens selected");
  }
  try {
    const responses = data.map((id) => {
      return apiClient.default.deleteApiV1TokensIdDelete({ id });
    });
    return await Promise.all(responses);
  } catch (error) {
    throw error;
  }
};

export const getEnrollmentRequests = async ({
  page,
  size,
}: Parameters<typeof apiClient.default.getRequestsApiV1RequestsGet>[0]) => {
  const response = await apiClient.default.getRequestsApiV1RequestsGet({ page, size });
  return response;
};

export type PostEnrollmentRequestsData = {
  ids: string[];
  accept: boolean;
};
export const postEnrollmentRequests = async (
  data: PendingSitesPostRequest,
): Promise<ReturnType<typeof apiClient.default.postRequestsApiV1RequestsPost>> => {
  if (!data?.ids || typeof data?.accept !== "boolean") {
    throw Error("Missing required fields");
  }
  try {
    const response = await apiClient.default.postRequestsApiV1RequestsPost({ requestBody: data });
    return response;
  } catch (error) {
    throw error;
  }
};

export const getCurrentUser = async () => {
  const response = await apiClient.default.getMeApiV1UsersMeGet();
  return response;
};

export type UserUpdateData = Omit<User, "id"> & { password: string; confirm_password: string };

export type UpdateUserPayload = {
  userId: number;
  userData: Partial<UserUpdateData>;
};

export const updateUser = ({ id, requestBody }: Parameters<typeof apiClient.default.patchApiV1UsersIdPatch>[0]) =>
  apiClient.default.patchApiV1UsersIdPatch({ id, requestBody });

export const addUser = ({ requestBody }: Parameters<typeof apiClient.default.postApiV1UsersPost>[0]) =>
  apiClient.default.postApiV1UsersPost({ requestBody });

export const deleteUser = ({ id }: Parameters<typeof apiClient.default.deleteApiV1UsersIdDelete>[0]) =>
  apiClient.default.deleteApiV1UsersIdDelete({ id });
