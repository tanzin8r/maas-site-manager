import type { BootAsset, ValidationErrorResponseModel } from "@/apiclient";

// TODO: replace with auto-generated type BootAsset when the missing fields are added
export type Image = BootAsset & {
  size: number;
  downloaded: number;
  is_custom_image: boolean;
};

// TODO: replace with auto-generated types from the API client https://warthogs.atlassian.net/browse/MAASENG-2569
export type UpstreamImage = Pick<Image, "id" | "release" | "arch" | "codename" | "size">;
export type UpstreamImageSource = {
  upstreamSource: string;
  keepUpdated: boolean;
  credentials: string;
};

export type MutationErrorResponse = {
  body: ValidationErrorResponseModel;
};
