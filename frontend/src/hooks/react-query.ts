import type { UseMutationOptions, UseMutationResult } from "@tanstack/react-query";
import { useQueryClient, useMutation, useQuery } from "@tanstack/react-query";
import type { AxiosError } from "axios";

import type {
  GetEnrollmentRequestsQueryParams,
  GetSitesQueryParams,
  GetTokensQueryParams,
  PostEnrollmentRequestsData,
  PostLoginData,
} from "@/api/handlers";
import {
  deleteTokens,
  postLogin,
  postEnrollmentRequests,
  getEnrollmentRequests,
  postTokens,
  getSites,
  getTokens,
} from "@/api/handlers";
import type {
  SitesQueryResult,
  PostTokensResult,
  EnrollmentRequestsQueryResult,
  AccessToken,
  Token,
  Site,
} from "@/api/types";

export type UseSitesQueryResult = ReturnType<typeof useSitesQuery>;

// 30 seconds
const defaultRefetchInterval = 30 * 1000;
export const useSitesQuery = ({ page, size }: GetSitesQueryParams, queryText?: string) =>
  useQuery<SitesQueryResult>({
    queryKey: ["sites", page, size, queryText],
    queryFn: () => getSites({ page, size }, queryText),
    keepPreviousData: true,
    refetchInterval: defaultRefetchInterval,
  });

// return single site data from query cache
export const useSiteQueryData = (id: Site["id"]): Site | null => {
  const queryClient = useQueryClient();
  // query cache data for all pages
  // this is to ensure we can request a site that is not on the current page
  const queryDataList = queryClient.getQueriesData<SitesQueryResult>({
    queryKey: ["sites"],
    exact: false,
    type: "all",
  });
  // reduce to a single list
  const sites = queryDataList.reduce((acc, [_key, data]) => [...acc, ...(data?.items ?? [])], [] as Site[]);
  const site = sites.find((site: any) => site.id === id);
  return site || null;
};

export type useTokensQueryResult = ReturnType<typeof useTokensQuery>;
export const useTokensQuery = ({ page, size }: GetTokensQueryParams) =>
  useQuery<PostTokensResult>({
    queryKey: ["tokens", page, size],
    queryFn: () => getTokens({ page, size }),
    keepPreviousData: true,
  });

export const useTokensCreateMutation = () => {
  const queryClient = useQueryClient();
  return useMutation(postTokens, {
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["tokens"] });
    },
  });
};

export const useDeleteTokensMutation = (options: UseMutationOptions<unknown, unknown, Token["id"][], unknown>) => {
  const queryClient = useQueryClient();
  return useMutation(deleteTokens, {
    ...options,
    onSuccess: (...args) => {
      options?.onSuccess?.(...args);
      queryClient.invalidateQueries({ queryKey: ["tokens"] });
    },
  });
};

export type UseEnrollmentRequestsQueryResult = ReturnType<typeof useRequestsQuery>;
export const useRequestsQuery = ({ page, size }: GetEnrollmentRequestsQueryParams) =>
  useQuery<EnrollmentRequestsQueryResult>({
    queryKey: ["requests", page, size],
    queryFn: () => getEnrollmentRequests({ page, size }),
    keepPreviousData: true,
    refetchInterval: defaultRefetchInterval,
  });

export const useRequestsCountQuery = () =>
  useQuery<EnrollmentRequestsQueryResult>({
    queryKey: ["requests", "1", "1"],
    queryFn: () => getEnrollmentRequests({ page: "1", size: "1" }),
    keepPreviousData: true,
    refetchInterval: defaultRefetchInterval,
  });

export const useEnrollmentRequestsMutation = (
  options: UseMutationOptions<unknown, unknown, PostEnrollmentRequestsData, unknown>,
) => {
  const queryClient = useQueryClient();
  return useMutation(postEnrollmentRequests, {
    onSuccess: (...args) => {
      queryClient.invalidateQueries({ queryKey: ["requests"] });
      options?.onSuccess?.(...args);
    },
  });
};
export type ApiError = AxiosError<{
  detail?: string | Array<{ loc: string[]; msg: string; type: string }>;
}>;
export type LoginError = ApiError;
export const useLoginMutation = (): UseMutationResult<AccessToken, LoginError, PostLoginData> => useMutation(postLogin);
