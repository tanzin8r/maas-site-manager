import type { MutateOptions, UseMutationOptions } from "@tanstack/react-query";
import { useQueryClient, useMutation, useQuery } from "@tanstack/react-query";

import type apiClient from "@/api";
import {
  deleteTokens,
  postLogin,
  postEnrollmentRequests,
  getEnrollmentRequests,
  postTokens,
  getSites,
  getTokens,
  getCurrentUser,
  updateUser,
  getUsers,
  addUser,
  getUser,
  getSite,
  getSitesCoordinates,
  deleteUser,
  getTokensExport,
  deleteSites,
} from "@/api/handlers";
import type { SitesQueryResult, PostTokensResult, Site, UsersQueryResult, User } from "@/api/types";
import type { PendingSitesPostRequest } from "@/api-client";
import { saveToFile } from "@/utils";

export type UseSitesQueryResult = ReturnType<typeof useSitesQuery>;

const refetchInterval = Number(import.meta.env.VITE_POLLING_INTERVAL_MS);

// TODO: integrate supported API params https://warthogs.atlassian.net/browse/MAASENG-2081
export const useSitesQuery = ({ page, size, sortBy }: Parameters<typeof apiClient.default.getApiV1SitesGet>[0]) =>
  useQuery<SitesQueryResult>({
    queryKey: ["sites", page, size, sortBy],
    queryFn: () => getSites({ page, size, sortBy }),
    keepPreviousData: true,
    refetchInterval,
  });

export const useSitesCoordinatesQuery = (queryText?: string) =>
  useQuery({
    queryKey: ["sitesCoordinates", queryText],
    queryFn: () => getSitesCoordinates(queryText),
    keepPreviousData: true,
    refetchInterval,
  });
export const useSiteQuery = ({ id }: Parameters<typeof apiClient.default.getIdApiV1SitesIdGet>[0]) =>
  useQuery<Site>({ queryKey: ["sites", id], queryFn: () => getSite({ id }), keepPreviousData: true });

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

export const useDeleteSitesMutation = (options?: UseMutationOptions<unknown, unknown, Site["id"][], unknown>) => {
  const queryClient = useQueryClient();
  return useMutation(deleteSites, {
    ...options,
    onSuccess: (...args) => {
      options?.onSuccess?.(...args);
      queryClient.invalidateQueries({ queryKey: ["sites"] });
    },
  });
};

export type useUsersQueryResult = ReturnType<typeof useUsersQuery>;
export const useUsersQuery = ({
  page,
  size,
  sortBy,
  searchText,
}: Parameters<typeof apiClient.default.getApiV1UsersGet>[0]) =>
  useQuery<UsersQueryResult>({
    queryKey: ["users", page, size, sortBy, searchText],
    queryFn: () => getUsers({ page, size, sortBy, searchText }),
    keepPreviousData: true,
  });

export type useUserQueryResult = ReturnType<typeof useUserQuery>;
export const useUserQuery = ({ id, enabled = true }: { id: User["id"]; enabled?: boolean }) =>
  useQuery<User>({
    queryKey: ["users", id],
    queryFn: () => getUser({ id }),
    keepPreviousData: true,
    enabled,
  });

export type useTokensQueryResult = ReturnType<typeof useTokensQuery>;
export const useTokensQuery = ({ page, size }: Parameters<typeof getTokens>[0]) =>
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

export const useExportTokensToFileQuery = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const exportTokens = async () => {
    setError(null);
    setIsLoading(true);
    getTokensExport()
      .then((data) => {
        if (data) {
          saveToFile(data, "site-manager-tokens.csv", "text/csv");
        }
        setIsLoading(false);
      })
      .catch((error) => {
        setError(error);
      });
  };

  return { error, isLoading, exportTokens };
};

export const useDeleteTokensMutation = (
  options?: Omit<UseMutationOptions<any, unknown, Parameters<typeof deleteTokens>[0], unknown>, "mutationFn">,
) => {
  const queryClient = useQueryClient();
  return useMutation(deleteTokens, {
    ...options,
    onSuccess: (...args) => {
      queryClient.invalidateQueries(["tokens"]);
      options?.onSuccess?.(...args);
    },
  });
};

export type UseEnrollmentRequestsQueryResult = ReturnType<typeof useRequestsQuery>;
export const useRequestsQuery = ({ page, size }: Parameters<typeof apiClient.default.getRequestsApiV1RequestsGet>[0]) =>
  useQuery({
    queryKey: ["requests", page, size],
    queryFn: () => getEnrollmentRequests({ page, size }),
    keepPreviousData: true,
    refetchInterval,
  });

export const useRequestsCountQuery = () =>
  useQuery({
    queryKey: ["requests", 1, 1],
    queryFn: () => getEnrollmentRequests({ page: 1, size: 1 }),
    keepPreviousData: true,
    refetchInterval,
  });

export const useEnrollmentRequestsMutation = (options: MutateOptions<unknown, unknown, PendingSitesPostRequest>) => {
  const queryClient = useQueryClient();
  return useMutation(postEnrollmentRequests, {
    onSuccess: (...args) => {
      queryClient.invalidateQueries({ queryKey: ["requests"] });
      options?.onSuccess?.(...args);
    },
  });
};

export const useLoginMutation = () => useMutation(postLogin);

export const useCurrentUserQuery = () => useQuery<User>({ queryKey: ["me"], queryFn: getCurrentUser });

export const useUpdateUserMutation = (
  options?: Omit<UseMutationOptions<any, unknown, Parameters<typeof updateUser>[0], unknown>, "mutationFn">,
) => useMutation(updateUser, options);

export const useAddUserMutation = (
  options?: Omit<
    UseMutationOptions<any, unknown, Parameters<typeof addUser>[0], Parameters<typeof addUser>[0]>,
    "mutationFn"
  >,
) => {
  const queryClient = useQueryClient();
  return useMutation(addUser, {
    ...options,
    onSuccess: (...args) => {
      queryClient.invalidateQueries(["users"]);
      options?.onSuccess?.(...args);
    },
  });
};

export const useDeleteUserMutation = (
  options?: Omit<UseMutationOptions<any, unknown, Parameters<typeof deleteUser>[0], unknown>, "mutationFn">,
) => {
  const queryClient = useQueryClient();
  return useMutation(deleteUser, {
    ...options,
    onSuccess: (...args) => {
      queryClient.invalidateQueries(["users"]);
      options?.onSuccess?.(...args);
    },
  });
};
