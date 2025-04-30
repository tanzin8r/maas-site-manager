import type { Options } from "@hey-api/client-axios";
import type { UseQueryOptions } from "@tanstack/react-query";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import type { AxiosError } from "axios";

import type {
  DeleteManyV1SitesDeleteData,
  DeleteManyV1SitesDeleteError,
  DeleteManyV1SitesDeleteResponse,
  GetCoordinatesV1SitesCoordinatesGetData,
  GetCoordinatesV1SitesCoordinatesGetError,
  GetCoordinatesV1SitesCoordinatesGetResponse,
  GetIdV1SitesIdGetData,
  GetIdV1SitesIdGetError,
  GetIdV1SitesIdGetResponse,
  GetV1SitesGetData,
  GetV1SitesGetError,
  GetV1SitesGetResponse,
  PatchV1SitesIdPatchData,
  PatchV1SitesIdPatchError,
  PatchV1SitesIdPatchResponse,
} from "@/apiclient";
import {
  deleteManyV1SitesDeleteMutation,
  getCoordinatesV1SitesCoordinatesGetOptions,
  getIdV1SitesIdGetOptions,
  getV1SitesGetOptions,
  getV1SitesGetQueryKey,
  patchV1SitesIdPatchMutation,
} from "@/apiclient/@tanstack/react-query.gen";

export const useSites = (options?: Options<GetV1SitesGetData>) => {
  return useQuery(
    getV1SitesGetOptions(options) as UseQueryOptions<GetV1SitesGetData, GetV1SitesGetError, GetV1SitesGetResponse>,
  );
};

export type UseSitesResult = ReturnType<typeof useSites>;

export const useSitesCoordinates = (options?: Options<GetCoordinatesV1SitesCoordinatesGetData>) => {
  return useQuery(
    getCoordinatesV1SitesCoordinatesGetOptions(options) as UseQueryOptions<
      GetCoordinatesV1SitesCoordinatesGetData,
      GetCoordinatesV1SitesCoordinatesGetError,
      GetCoordinatesV1SitesCoordinatesGetResponse
    >,
  );
};

export const useSite = (options: Options<GetIdV1SitesIdGetData>) => {
  return useQuery(
    getIdV1SitesIdGetOptions(options) as UseQueryOptions<
      GetIdV1SitesIdGetData,
      GetIdV1SitesIdGetError,
      GetIdV1SitesIdGetResponse
    >,
  );
};

export const useEditSite = (mutationOptions?: Options<PatchV1SitesIdPatchData>) => {
  const queryClient = useQueryClient();

  return useMutation<
    PatchV1SitesIdPatchResponse,
    AxiosError<PatchV1SitesIdPatchError>,
    Options<PatchV1SitesIdPatchData>
  >({
    ...patchV1SitesIdPatchMutation(mutationOptions),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: getV1SitesGetQueryKey() });
    },
  });
};

export const useDeleteSites = (mutationOptions?: Options<DeleteManyV1SitesDeleteData>) => {
  const queryClient = useQueryClient();

  return useMutation<
    DeleteManyV1SitesDeleteResponse,
    AxiosError<DeleteManyV1SitesDeleteError>,
    Options<DeleteManyV1SitesDeleteData>
  >({
    ...deleteManyV1SitesDeleteMutation(mutationOptions),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: getV1SitesGetQueryKey() });
    },
  });
};
