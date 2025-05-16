import type { Options } from "@hey-api/client-axios";
import type { UseQueryOptions } from "@tanstack/react-query";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import type { AxiosError } from "axios";

import type {
  GetV1SettingsGetData,
  GetV1SettingsGetError,
  GetV1SettingsGetResponse,
  PatchV1SettingsPatchData,
  PatchV1SettingsPatchError,
  PatchV1SettingsPatchResponses,
} from "@/apiclient";
import {
  getV1SettingsGetOptions,
  getV1SettingsGetQueryKey,
  patchV1SettingsPatchMutation,
} from "@/apiclient/@tanstack/react-query.gen";

export const useSettings = (options?: Options<GetV1SettingsGetData>) => {
  return useQuery(
    getV1SettingsGetOptions(options) as UseQueryOptions<
      GetV1SettingsGetData,
      GetV1SettingsGetError,
      GetV1SettingsGetResponse
    >,
  );
};

export type PatchV1SettingsPatchResponse = PatchV1SettingsPatchResponses[keyof PatchV1SettingsPatchResponses];

export const useUpdateSettings = (mutationOptions: Options<PatchV1SettingsPatchData>) => {
  const queryClient = useQueryClient();

  return useMutation<
    PatchV1SettingsPatchResponse,
    AxiosError<PatchV1SettingsPatchError>,
    Options<PatchV1SettingsPatchData>
  >({
    ...patchV1SettingsPatchMutation(mutationOptions),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: getV1SettingsGetQueryKey() });
    },
  });
};
