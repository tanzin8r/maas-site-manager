import type { UseMutationOptions, UseMutationResult } from "@tanstack/react-query";
import { useMutation, useQuery } from "@tanstack/react-query";
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
  patchEnrollmentRequests,
  getEnrollmentRequests,
  postTokens,
  getSites,
  getTokens,
} from "@/api/handlers";
import type { SitesQueryResult, PostTokensResult, EnrollmentRequestsQueryResult, AccessToken } from "@/api/types";

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

export type useTokensQueryResult = ReturnType<typeof useTokensQuery>;
export const useTokensQuery = ({ page, size }: GetTokensQueryParams) =>
  useQuery<PostTokensResult>({
    queryKey: ["tokens", page, size],
    queryFn: () => getTokens({ page, size }),
    keepPreviousData: true,
  });

export const useTokensMutation = () => useMutation(postTokens);

export const useDeleteTokensMutation = (options: UseMutationOptions<unknown, unknown, string[], unknown>) =>
  useMutation(deleteTokens, options);

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
    queryKey: ["requests", "0", "1"],
    queryFn: () => getEnrollmentRequests({ page: "0", size: "1" }),
    keepPreviousData: true,
    refetchInterval: defaultRefetchInterval,
  });

export const useEnrollmentRequestsMutation = (
  options: UseMutationOptions<unknown, unknown, PostEnrollmentRequestsData, unknown>,
) => useMutation(patchEnrollmentRequests, options);
export type ApiError = AxiosError<{
  detail?: string | Array<{ loc: string[]; msg: string; type: string }>;
}>;
export type LoginError = ApiError;
export const useLoginMutation = (): UseMutationResult<AccessToken, LoginError, PostLoginData> => useMutation(postLogin);
