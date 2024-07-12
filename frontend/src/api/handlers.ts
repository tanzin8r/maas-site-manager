import { apiClient } from "./api";

import type { Image, UpstreamImage, TSettings, TSettingsPatchRequest, UpstreamImageSource } from "@/api";
import type {
  Token,
  User,
  SitesGetResponse,
  Body_post_v1_login_post,
  PendingSitesPostRequest,
  TokensPostRequest,
  Site,
} from "@/api/client";
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

export const getSettings = async () => {
  try {
    const response = await apiClient.default.getV1SettingsGet();
    return response as TSettings;
  } catch (error) {
    throw error;
  }
};

export const updateSettings = async (data: TSettingsPatchRequest) => {
  try {
    const response = await apiClient.default.patchV1SettingsPatch({ requestBody: data });
    return response;
  } catch (error) {
    throw error;
  }
};

export type PaginationParams = Pick<SitesGetResponse, "page" | "size">;

export type SortDirection = "asc" | "desc";

export type SitesSortKey = "name";
export type UserSortKey = "username" | "full_name" | "email";
export type ImagesSortKey = "release";

export type SortBy<T extends SitesSortKey | UserSortKey | ImagesSortKey> = `${T}-${SortDirection}` | null;
export type SortingParams<T extends SitesSortKey | UserSortKey> = {
  sortBy: SortBy<T>;
};

export type GetSitesQueryParams = Parameters<typeof apiClient.default.getV1SitesGet>[0];

// TODO: integrate supported API params https://warthogs.atlassian.net/browse/MAASENG-2081
export const getSites = (params: Parameters<typeof apiClient.default.getV1SitesGet>[0]) =>
  apiClient.default.getV1SitesGet({
    missingCoordinates: params.missingCoordinates,
    page: Number(params.page),
    size: Number(params.size),
    sortBy: params.sortBy || null,
  });

// TODO: pass search params once API supports it https://warthogs.atlassian.net/browse/MAASENG-2080
export const getSitesCoordinates = async (_queryText?: string) =>
  apiClient.default.getCoordinatesV1SitesCoordinatesGet({});

export const getSite = async ({ id }: Parameters<typeof apiClient.default.getIdV1SitesIdGet>[0]) => {
  const response = await apiClient.default.getIdV1SitesIdGet({ id });
  return response;
};

export const updateSite = ({ id, requestBody }: Parameters<typeof apiClient.default.patchV1SitesIdPatch>[0]) =>
  apiClient.default.patchV1SitesIdPatch({ id, requestBody });

export const deleteSites = async ({ ids }: Parameters<typeof apiClient.default.deleteManyV1SitesDelete>[0]) =>
  apiClient.default.deleteManyV1SitesDelete({ ids });

export const updateSitesCoordinates = (data: Pick<Site, "id" | "coordinates">[]) => {
  if (data.length === 0) {
    throw Error("No sites selected");
  }
  try {
    const responses = data.map(({ id, coordinates }) => {
      return apiClient.default.patchV1SitesIdPatch({ id, requestBody: { coordinates } });
    });
    return Promise.allSettled(responses);
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

export const deleteTokens = async (data: Token["id"][]) => apiClient.default.deleteManyV1TokensDelete({ ids: data });

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
export const getImages = async (params: Record<string, number | string | null>) => {
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

// TODO: replace with api client once API supports it https://warthogs.atlassian.net/browse/MAASENG-2569
export const getUpstreamImages = async (params: Record<string, number>) => {
  let stringParams: Record<string, string> = {};
  for (const [key, value] of Object.entries(params)) {
    stringParams[key] = String(value);
  }
  const response = await fetch(`${apiUrls.upstreamImages}?${new URLSearchParams(stringParams)}`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
  });
  const data = (await response.json()) as { items: UpstreamImage[]; page: number; total: number; size: number };
  return data;
};

// TODO: replace with api client once API supports it https://warthogs.atlassian.net/browse/MAASENG-2569
export const getUpstreamImageSource = async () => {
  const response = await fetch(apiUrls.upstreamImageSource, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
  });

  const data = (await response.json()) as Omit<UpstreamImageSource, "credentials">;
  return data;
};

// TODO: replace with api client once API supports it https://warthogs.atlassian.net/browse/MAASENG-2569
export const updateUpstreamImageSource = async (payload: UpstreamImageSource) => {
  try {
    const response = await fetch(apiUrls.upstreamImageSource, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });

    return response;
  } catch (error) {
    throw error;
  }
};

export type SelectUpstreamImagesPayload = {
  id: UpstreamImage["id"];
  download: boolean;
};

// TODO: replace with api client once API supports it https://warthogs.atlassian.net/browse/MAASENG-2569
export const selectUpstreamImages = async (payload: SelectUpstreamImagesPayload[]) => {
  try {
    const response = await fetch(apiUrls.upstreamImages, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });

    return response;
  } catch (error) {
    throw error;
  }
};

// TODO: replace with api client once API supports it https://warthogs.atlassian.net/browse/MAASENG-2638
export const deleteImages = async (data: Image["id"][]) => {
  if (data.length === 0) {
    throw Error("No images selected");
  }
  try {
    const responses = data.map((id) => {
      return fetch(`${apiUrls.images}/${id}`, {
        method: "DELETE",
        headers: {
          "Content-Type": "application/json",
        },
      });
    });
    return await Promise.allSettled(responses);
  } catch (error) {
    throw error;
  }
};

export type UploadImagePayload = {
  image: File;
  imageId: string;
  release: string;
  title: string;
  baseImage?: string;
  architecture: string;
};

// TODO: replace with api client once API supports it https://warthogs.atlassian.net/browse/MAASENG-2715
export const uploadImage = async (payload: UploadImagePayload) => {
  try {
    const response = await fetch(apiUrls.images, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });

    return response;
  } catch (error) {
    throw error;
  }
};
