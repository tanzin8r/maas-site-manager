import type { Settings, SettingsPatchRequest } from "@/api/client";

// TODO: replace with auto-generated types from the API client https://warthogs.atlassian.net/browse/MAASENG-2570
export type Image = {
  id: number;
  release: string;
  architecture: string;
  name: string;
  size: number;
  downloaded: number;
  number_of_sites_synced: number;
  is_custom_image: boolean;
  last_synced: string | null; // <ISO 8601 date string>
};

// TODO: replace with auto-generated types from the API client https://warthogs.atlassian.net/browse/MAASENG-2569
export type UpstreamImage = Pick<Image, "id" | "release" | "architecture" | "name" | "size">;
export type UpstreamImageSource = {
  upstreamSource: string;
  keepUpdated: boolean;
  credentials: string;
};

// TODO: replace with actual Settings type
// once settings api is updated
// https://warthogs.atlassian.net/browse/MAASENG-2594
export type TSettings = Settings & { images_connect_to_maas: boolean };

// TODO: replace with actual SettingsPatchRequest type
// once settings api is updated
// https://warthogs.atlassian.net/browse/MAASENG-2594
export type TSettingsPatchRequest = SettingsPatchRequest & { images_connect_to_maas: boolean };
