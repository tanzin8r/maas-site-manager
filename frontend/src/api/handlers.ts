import type { Site, User } from "../apiclient";

import { apiClient } from "./api";

import type { Image, UpstreamImage, UpstreamImageSource } from "@/api";
import { maxPageSize, minPageSize } from "@/components/base/PaginationBar";
import { apiUrls } from "@/utils/test-urls";

export type SortDirection = "asc" | "desc";

export type SitesSortKey = keyof Pick<Site, "name">;
export type UserSortKey = keyof Pick<User, "username" | "full_name" | "email">;
export type ImagesSortKey = keyof Pick<Image, "release">;

export type SortBy<T extends SitesSortKey | UserSortKey | ImagesSortKey> = `${T}-${SortDirection}` | null;

export const getTokensExport = async (
  parameters: Parameters<typeof apiClient.default.getExportV1TokensExportGet>[0],
) => {
  try {
    const id = parameters.id;
    if (id?.length) {
      // we have id filters, thus the user selected from a page and we do not need to return more than maxPageSize
      const response = await apiClient.default.getExportV1TokensExportGet({ page: 1, size: maxPageSize, id: id });
      return response;
    } else {
      // we are exporting all tokens. We might need to return the results from multiple pages
      const totalTokens: number = (await apiClient.default.getV1TokensGet({ page: 1, size: minPageSize })).total;
      const pagesToLoad: number = totalTokens / maxPageSize;
      const requests = [];
      for (let page: number = 1; page <= pagesToLoad + 1; page++) {
        requests.push(apiClient.default.getExportV1TokensExportGet({ page: page, size: maxPageSize }));
      }
      const responses = await Promise.all(requests);
      const newLines = /\r\n|\r|\n/g; // catch newlines of type \r, \n and \r\n
      const header: string = responses[0].split(newLines)[0];
      const pages: string = responses
        .map((response) => {
          const lines = response.split(newLines);
          lines.shift();
          return lines.join("\n");
        })
        .join("");
      return [header, pages].join("\n");
    }
  } catch (error) {
    throw error;
  }
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
