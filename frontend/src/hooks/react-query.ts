import type { UseMutationOptions } from "@tanstack/react-query";
import { keepPreviousData, useInfiniteQuery, useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import apiClient from "@/api";
import type { BootAsset } from "@/api";
import {
  getTokensExport,
  getUpstreamImages,
  updateUpstreamImageSource,
  selectUpstreamImages,
  getUpstreamImageSource,
  deleteImages,
  uploadImage,
} from "@/api/handlers";
import { saveToFile } from "@/utils";

const refetchInterval = Number(import.meta.env.VITE_POLLING_INTERVAL_MS);

export const useExportTokensToFileQuery = ({ id }: Parameters<typeof apiClient.default.getV1TokensGet>[0]) => {
  const [isPending, setisPending] = useState(false);
  const [error, setError] = useState<unknown | null>(null);

  const exportTokens = async (parameters: Parameters<typeof getTokensExport>[0]) => {
    setError(null);
    setisPending(true);
    getTokensExport({ ...parameters, id: id })
      .then((data) => {
        if (data) {
          saveToFile(data, "site-manager-tokens.csv", "text/csv");
        }
        setisPending(false);
      })
      .catch((error) => {
        setError(error);
      });
  };

  return { error, isPending, exportTokens };
};

const DEFAULT_PAGE_SIZE = 10;
export const useImagesInfiniteQuery = ({
  sortBy,
  pageSize = DEFAULT_PAGE_SIZE,
}: {
  sortBy: string | null;
  pageSize?: number;
}) => {
  const query = useInfiniteQuery({
    queryKey: ["images", sortBy, pageSize],
    initialPageParam: { page: 1, size: pageSize },
    refetchInterval,
    queryFn: ({ pageParam: { page } }) =>
      apiClient.default.getBootAssetsV1BootassetsGet({ page, size: pageSize, sortBy }),
    getNextPageParam: (lastPage, allPages) => {
      if (!lastPage) return undefined;
      const fetchedItemsCount = allPages.reduce((total, page) => total + page.items.length, 0);
      return fetchedItemsCount < lastPage.total ? { page: lastPage.page + 1, size: DEFAULT_PAGE_SIZE } : undefined;
    },
    staleTime: Infinity,
  });

  const data = {
    items: query.data?.pages ? query.data.pages.reduce((acc, page) => acc.concat(page.items), [] as BootAsset[]) : [],
  };

  const { hasNextPage, isFetchingNextPage, fetchNextPage } = query;

  useEffect(() => {
    if (hasNextPage && !isFetchingNextPage) {
      fetchNextPage();
    }
  }, [hasNextPage, isFetchingNextPage, fetchNextPage]);

  return { ...query, data };
};

export const useUpstreamImagesQuery = ({ page, size }: Record<string, number>) =>
  useQuery({
    queryKey: ["upstreamImages", page, size],
    queryFn: () => getUpstreamImages({ page, size }),
    placeholderData: keepPreviousData,
    refetchInterval,
  });

export const useUpstreamImageSourceQuery = () =>
  useQuery({
    queryKey: ["upstreamImageSource"],
    queryFn: getUpstreamImageSource,
    placeholderData: keepPreviousData,
    refetchInterval,
  });

export const useUpstreamImageSourceMutation = (
  options?: Omit<
    UseMutationOptions<any, unknown, Parameters<typeof updateUpstreamImageSource>[0], unknown>,
    "mutationFn"
  >,
) => {
  return useMutation({
    mutationFn: updateUpstreamImageSource,
    ...options,
    onSuccess: (...args) => {
      options?.onSuccess?.(...args);
    },
  });
};

export const useSelectUpstreamImagesMutation = (
  options?: Omit<UseMutationOptions<any, unknown, Parameters<typeof selectUpstreamImages>[0], unknown>, "mutationFn">,
) => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: selectUpstreamImages,
    ...options,
    onSuccess: (...args) => {
      queryClient.invalidateQueries({ queryKey: ["images"] });
      options?.onSuccess?.(...args);
    },
  });
};

export const useDeleteImagesMutation = (
  options?: Omit<UseMutationOptions<any, unknown, Parameters<typeof deleteImages>[0], unknown>, "mutationFn">,
) => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: deleteImages,
    ...options,
    onSuccess: (...args) => {
      queryClient.invalidateQueries({ queryKey: ["images"] });
      options?.onSuccess?.(...args);
    },
    onError: () => {
      queryClient.invalidateQueries({ queryKey: ["images"] });
    },
  });
};

export const useUploadImageMutation = (
  options?: Omit<UseMutationOptions<any, unknown, Parameters<typeof uploadImage>[0], unknown>, "mutationFn">,
) => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: uploadImage,
    ...options,
    onSuccess: (...args) => {
      queryClient.invalidateQueries({ queryKey: ["images", "upstreamImages"] });
      options?.onSuccess?.(...args);
    },
  });
};
