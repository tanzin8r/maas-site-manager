import { apiClient } from "./api";
import type { Token, User } from "./types";

import type {
  SitesGetResponse,
  Body_post_v1_login_post,
  PendingSitesPostRequest,
  Site,
  TokensPostRequest,
} from "@/api-client";
import type { Image } from "@/mocks/factories";
import { apiUrls } from "@/utils/test-urls";

export const postLogin = async (data: Body_post_v1_login_post) => {
  if (!data?.username || !data?.password) {
    throw Error("Missing required fields");
  }
  try {
    const response = await apiClient.default.postV1LoginPost({ formData: data });
    return response;
  } catch (error) {
    throw error;
  }
};

export type PaginationParams = Pick<SitesGetResponse, "page" | "size">;

export type SortDirection = "asc" | "desc";

export type SitesSortKey = "name";
export type UserSortKey = "username" | "full_name" | "email";

export type SortBy<T extends SitesSortKey | UserSortKey> = `${T}-${SortDirection}` | null;
export type SortingParams<T extends SitesSortKey | UserSortKey> = {
  sortBy: SortBy<T>;
};

export type GetSitesQueryParams = Parameters<typeof apiClient.default.getV1SitesGet>[0];

// TODO: integrate supported API params https://warthogs.atlassian.net/browse/MAASENG-2081
export const getSites = (params: Parameters<typeof apiClient.default.getV1SitesGet>[0]) =>
  apiClient.default.getV1SitesGet({
    page: Number(params.page),
    size: Number(params.size),
    sortBy: params.sortBy || null,
  });

// TODO: pass search params once API supports it https://warthogs.atlassian.net/browse/MAASENG-2080
export const getSitesCoordinates = async (_queryText?: string) =>
  apiClient.default.getCoordinatesV1SitesCoordinatesGet();

export const getSite = async ({ id }: Parameters<typeof apiClient.default.getIdV1SitesIdGet>[0]) => {
  const response = await apiClient.default.getIdV1SitesIdGet({ id });
  return response;
};

export const updateSite = ({ id, requestBody }: Parameters<typeof apiClient.default.patchV1SitesIdPatch>[0]) =>
  apiClient.default.patchV1SitesIdPatch({ id, requestBody });

export const deleteSites = async (data: Site["id"][]) => {
  if (data.length === 0) {
    throw Error("No sites selected");
  }
  try {
    const responses = data.map((id) => {
      return apiClient.default.deleteV1SitesIdDelete({ id });
    });
    return await Promise.allSettled(responses);
  } catch (error) {
    throw error;
  }
};

export const postTokens = async (data: TokensPostRequest) => {
  if (!data?.count || !data?.duration) {
    throw Error("Missing required fields");
  }
  try {
    const response = await apiClient.default.postV1TokensPost({ requestBody: data });
    return response;
  } catch (error) {
    throw error;
  }
};

export const getTokensExport = async () => {
  try {
    const response = await apiClient.default.getExportV1TokensExportGet();
    return response;
  } catch (error) {
    throw error;
  }
};

export type GetTokensQueryParams = PaginationParams & {};
export const getTokens = ({ page, size }: Parameters<typeof apiClient.default.getV1TokensGet>[0]) =>
  apiClient.default.getV1TokensGet({ page, size });

export const getUsers = async (params: Parameters<typeof apiClient.default.getV1UsersGet>[0]) => {
  try {
    const response = await apiClient.default.getV1UsersGet({
      ...params,
    });
    return response;
  } catch (error) {
    throw error;
  }
};

export const getUser = async ({ id }: Parameters<typeof apiClient.default.getIdV1UsersIdGet>[0]) => {
  const response = await apiClient.default.getIdV1UsersIdGet({ id });
  return response;
};

export const deleteTokens = async (data: Token["id"][]) => {
  if (data.length === 0) {
    throw Error("No tokens selected");
  }
  try {
    const responses = data.map((id) => {
      return apiClient.default.deleteV1TokensIdDelete({ id });
    });
    return await Promise.allSettled(responses);
  } catch (error) {
    throw error;
  }
};

export const getEnrollmentRequests = async ({
  page,
  size,
}: Parameters<typeof apiClient.default.getPendingV1SitesPendingGet>[0]) => {
  const response = await apiClient.default.getPendingV1SitesPendingGet({ page, size });
  return response;
};

export type PostEnrollmentRequestsData = {
  ids: string[];
  accept: boolean;
};
export const postEnrollmentRequests = async (
  data: PendingSitesPostRequest,
): Promise<ReturnType<typeof apiClient.default.postPendingV1SitesPendingPost>> => {
  if (!data?.ids || typeof data?.accept !== "boolean") {
    throw Error("Missing required fields");
  }
  try {
    const response = await apiClient.default.postPendingV1SitesPendingPost({ requestBody: data });
    return response;
  } catch (error) {
    throw error;
  }
};

export const getCurrentUser = async () => {
  const response = await apiClient.default.getMeV1UsersMeGet();
  return response;
};

export type UserUpdateData = Omit<User, "id"> & { password: string; confirm_password: string };

export type UpdateUserPayload = {
  userId: number;
  userData: Partial<UserUpdateData>;
};

export const updateUser = ({ id, requestBody }: Parameters<typeof apiClient.default.patchV1UsersIdPatch>[0]) =>
  apiClient.default.patchV1UsersIdPatch({ id, requestBody });

export const addUser = ({ requestBody }: Parameters<typeof apiClient.default.postV1UsersPost>[0]) =>
  apiClient.default.postV1UsersPost({ requestBody });

export const deleteUser = ({ id }: Parameters<typeof apiClient.default.deleteV1UsersIdDelete>[0]) =>
  apiClient.default.deleteV1UsersIdDelete({ id });

// TODO: replace with api client once API supports it https://warthogs.atlassian.net/browse/MAASENG-2570
export const getImages = async (params: Record<string, number>) => {
  let stringParams: Record<string, string> = {};
  for (const [key, value] of Object.entries(params)) {
    stringParams[key] = String(value);
  }
  const response = await fetch(`${apiUrls.images}?${new URLSearchParams(stringParams)}`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
  });
  const data = (await response.json()) as { items: Image[]; page: number; total: number; size: number };
  return data;
};
