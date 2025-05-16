import type { Site, User } from "../apiclient";

import type { Image, UpstreamImage, UpstreamImageSource } from "@/api";
import { apiUrls } from "@/utils/test-urls";

export type SortDirection = "asc" | "desc";

export type SitesSortKey = keyof Pick<Site, "name">;
export type UserSortKey = keyof Pick<User, "username" | "full_name" | "email">;
export type ImagesSortKey = keyof Pick<Image, "release">;

export type SortBy<T extends SitesSortKey | UserSortKey | ImagesSortKey> = `${T}-${SortDirection}` | null;

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

  if (!response.ok) {
    throw new Error("Failed to fetch upstream image source");
  }

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
  const response = await fetch(apiUrls.upstreamImages, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    throw new Error("Failed to select upstream images");
  }
};

// TODO: replace with api client once API supports it https://warthogs.atlassian.net/browse/MAASENG-2638
export const deleteImages = async (data: Image["id"][]) => {
  if (data.length === 0) {
    throw Error("No images selected");
  }
  try {
    const responses = data.map((id) => {
      return fetch(`${apiUrls.bootAssets}/${id}`, {
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
  const response = await fetch(apiUrls.bootAssets, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw new Error("Failed to upload image");
  }

  return response;
};
