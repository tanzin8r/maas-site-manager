import { useMutation, useQuery } from "@tanstack/react-query";

import type { GetSitesQueryParams, GetTokensQueryParams } from "@/api/handlers";
import { postTokens, getSites, getTokens } from "@/api/handlers";
import type { SitesQueryResult, PostTokensResult } from "@/api/types";

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
