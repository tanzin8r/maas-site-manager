import type { Options } from "@hey-api/client-axios";
import type { UseQueryOptions } from "@tanstack/react-query";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import type { AxiosError } from "axios";

import {
  type PostV1TokensPostResponse,
  type GetV1TokensGetData,
  type GetV1TokensGetError,
  type GetV1TokensGetResponse,
  type PostV1TokensPostData,
  type PostV1TokensPostError,
  type DeleteManyV1TokensDeleteData,
  type DeleteManyV1TokensDeleteResponse,
  type DeleteManyV1TokensDeleteError,
} from "@/apiclient";
import {
  deleteManyV1TokensDeleteMutation,
  getV1TokensGetOptions,
  getV1TokensGetQueryKey,
  postV1TokensPostMutation,
} from "@/apiclient/@tanstack/react-query.gen";

export const useTokens = (options?: Options<GetV1TokensGetData>) => {
  return useQuery(
    getV1TokensGetOptions(options) as UseQueryOptions<GetV1TokensGetData, GetV1TokensGetError, GetV1TokensGetResponse>,
  );
};

export type UseTokensResult = ReturnType<typeof useTokens>;

export const useCreateTokens = (mutationOptions?: Options<PostV1TokensPostData>) => {
  const queryClient = useQueryClient();

  return useMutation<PostV1TokensPostResponse, AxiosError<PostV1TokensPostError>, Options<PostV1TokensPostData>>({
    ...postV1TokensPostMutation(mutationOptions),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: getV1TokensGetQueryKey() });
    },
  });
};

export const useDeleteTokens = (mutationOptions?: Options<DeleteManyV1TokensDeleteData>) => {
  const queryClient = useQueryClient();

  return useMutation<
    DeleteManyV1TokensDeleteResponse,
    AxiosError<DeleteManyV1TokensDeleteError>,
    Options<DeleteManyV1TokensDeleteData>
  >({
    ...deleteManyV1TokensDeleteMutation(mutationOptions),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: getV1TokensGetQueryKey() });
    },
  });
};
