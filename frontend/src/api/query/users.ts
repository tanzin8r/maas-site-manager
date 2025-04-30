import type { Options } from "@hey-api/client-axios";
import type { UseQueryOptions } from "@tanstack/react-query";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import type { AxiosError } from "axios";

import type {
  PatchV1UsersIdPatchError,
  PatchV1UsersIdPatchResponse,
  GetV1UsersGetData,
  GetV1UsersGetError,
  GetV1UsersGetResponse,
  PatchV1UsersIdPatchData,
  PostV1UsersPostData,
  PostV1UsersPostError,
  PostV1UsersPostResponse,
  GetIdV1UsersIdGetData,
  GetIdV1UsersIdGetError,
  GetIdV1UsersIdGetResponse,
  GetMeV1UsersMeGetData,
  GetMeV1UsersMeGetError,
  PatchMeV1UsersMePatchData,
  PatchMeV1UsersMePatchResponse,
  PatchMeV1UsersMePatchError,
  DeleteV1UsersIdDeleteData,
  DeleteV1UsersIdDeleteResponse,
  DeleteV1UsersIdDeleteError,
  PatchMePasswordV1UsersMePasswordPatchData,
  PatchMePasswordV1UsersMePasswordPatchResponses,
  PatchMePasswordV1UsersMePasswordPatchError,
  GetMeV1UsersMeGetResponse,
} from "@/apiclient";
import {
  deleteV1UsersIdDeleteMutation,
  getIdV1UsersIdGetOptions,
  getMeV1UsersMeGetOptions,
  getMeV1UsersMeGetQueryKey,
  getV1UsersGetOptions,
  getV1UsersGetQueryKey,
  patchMePasswordV1UsersMePasswordPatchMutation,
  patchMeV1UsersMePatchMutation,
  patchV1UsersIdPatchMutation,
  postV1UsersPostMutation,
} from "@/apiclient/@tanstack/react-query.gen";

export const useUsers = (options?: Options<GetV1UsersGetData>) => {
  return useQuery(
    getV1UsersGetOptions(options) as UseQueryOptions<GetV1UsersGetData, GetV1UsersGetError, GetV1UsersGetResponse>,
  );
};

export type UseUsersResult = ReturnType<typeof useUsers>;

export const useUser = (options: Options<GetIdV1UsersIdGetData>, enabled = true) => {
  return useQuery({
    ...(getIdV1UsersIdGetOptions(options) as UseQueryOptions<
      GetIdV1UsersIdGetData,
      GetIdV1UsersIdGetError,
      GetIdV1UsersIdGetResponse
    >),
    enabled,
  });
};

export const useCurrentUser = (options?: Options<GetMeV1UsersMeGetData>) => {
  return useQuery(
    getMeV1UsersMeGetOptions(options) as UseQueryOptions<
      GetMeV1UsersMeGetData,
      GetMeV1UsersMeGetError,
      GetMeV1UsersMeGetResponse
    >,
  );
};

export const useAddUser = (mutationOptions?: Options<PostV1UsersPostData>) => {
  const queryClient = useQueryClient();

  return useMutation<PostV1UsersPostResponse, AxiosError<PostV1UsersPostError>, Options<PostV1UsersPostData>>({
    ...postV1UsersPostMutation(mutationOptions),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: getV1UsersGetQueryKey() });
    },
  });
};

export const useEditUser = (mutationOptions?: Options<PatchV1UsersIdPatchData>) => {
  const queryClient = useQueryClient();

  return useMutation<
    PatchV1UsersIdPatchResponse,
    AxiosError<PatchV1UsersIdPatchError>,
    Options<PatchV1UsersIdPatchData>
  >({
    ...patchV1UsersIdPatchMutation(mutationOptions),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: getV1UsersGetQueryKey() });
    },
  });
};

export const useEditCurrentUser = (mutationOptions?: Options<PatchMeV1UsersMePatchData>) => {
  const queryClient = useQueryClient();

  return useMutation<
    PatchMeV1UsersMePatchResponse,
    AxiosError<PatchMeV1UsersMePatchError>,
    Options<PatchMeV1UsersMePatchData>
  >({
    ...patchMeV1UsersMePatchMutation(mutationOptions),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: getV1UsersGetQueryKey() });
      queryClient.invalidateQueries({ queryKey: getMeV1UsersMeGetQueryKey() });
    },
  });
};

export const useChangePassword = (mutationOptions?: Options<PatchMePasswordV1UsersMePasswordPatchData>) => {
  return useMutation<
    // the client doesn't have a constructed type for this, so we have to do it manually.
    PatchMePasswordV1UsersMePasswordPatchResponses[keyof PatchMePasswordV1UsersMePasswordPatchResponses],
    AxiosError<PatchMePasswordV1UsersMePasswordPatchError>,
    Options<PatchMePasswordV1UsersMePasswordPatchData>
  >({
    ...patchMePasswordV1UsersMePasswordPatchMutation(mutationOptions),
  });
};

export const useDeleteUser = (mutationOptions?: Options<DeleteV1UsersIdDeleteData>) => {
  const queryClient = useQueryClient();

  return useMutation<
    DeleteV1UsersIdDeleteResponse,
    AxiosError<DeleteV1UsersIdDeleteError>,
    Options<DeleteV1UsersIdDeleteData>
  >({
    ...deleteV1UsersIdDeleteMutation(mutationOptions),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: getV1UsersGetQueryKey() });
    },
  });
};
