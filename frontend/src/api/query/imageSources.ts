import { useInfiniteQuery, useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import type {
  BootSource,
  DeleteBootSourceV1BootassetSourcesIdDeleteData,
  GetBootSourceByIdV1BootassetSourcesIdGetData,
  GetBootSourcesV1BootassetSourcesGetData,
  Options,
  PatchBootSourceV1BootassetSourcesIdPatchData,
  PostBootSourcesV1BootassetSourcesPostData,
} from "@/apiclient";
import {
  deleteBootSourceV1BootassetSourcesIdDeleteMutation,
  getBootSourceByIdV1BootassetSourcesIdGetOptions,
  getBootSourceByIdV1BootassetSourcesIdGetQueryKey,
  getBootSourcesV1BootassetSourcesGetInfiniteOptions,
  getBootSourcesV1BootassetSourcesGetInfiniteQueryKey,
  getBootSourcesV1BootassetSourcesGetQueryKey,
  patchBootSourceV1BootassetSourcesIdPatchMutation,
  postBootSourcesV1BootassetSourcesPostMutation,
} from "@/apiclient/@tanstack/react-query.gen";

const DEFAULT_PAGE_SIZE = 10;
const refetchInterval = Number(import.meta.env.VITE_POLLING_INTERVAL_MS);

export const useImageSources = (options?: Options<GetBootSourcesV1BootassetSourcesGetData>) => {
  const defaultOptions: Options<GetBootSourcesV1BootassetSourcesGetData> = {
    query: {
      page: 1,
      size: DEFAULT_PAGE_SIZE,
    },
  };

  const query = useInfiniteQuery({
    ...getBootSourcesV1BootassetSourcesGetInfiniteOptions(options),
    initialPageParam: defaultOptions,
    refetchInterval,
    getNextPageParam: (lastPage, allPages): Options<GetBootSourcesV1BootassetSourcesGetData> | undefined => {
      if (!lastPage) return undefined;
      const fetchedItemsCount = allPages.reduce((total, page) => total + page.items.length, 0);
      return fetchedItemsCount < lastPage.total
        ? {
            query: {
              page: lastPage.page + 1,
              size: DEFAULT_PAGE_SIZE,
            },
          }
        : undefined;
    },
  });

  const data = {
    items: query.data?.pages ? query.data.pages.reduce((acc, page) => acc.concat(page.items), [] as BootSource[]) : [],
  };
  const { hasNextPage, isFetchingNextPage, fetchNextPage } = query;

  useEffect(() => {
    if (hasNextPage && !isFetchingNextPage) {
      void fetchNextPage();
    }
  }, [hasNextPage, isFetchingNextPage, fetchNextPage]);

  return { ...query, data };
};

export const useImageSource = (options: Options<GetBootSourceByIdV1BootassetSourcesIdGetData>, enabled = true) => {
  return useQuery({
    ...getBootSourceByIdV1BootassetSourcesIdGetOptions(options),
    enabled,
  });
};

export const useCreateImageSource = (mutationOptions?: Options<PostBootSourcesV1BootassetSourcesPostData>) => {
  const queryClient = useQueryClient();
  return useMutation({
    ...postBootSourcesV1BootassetSourcesPostMutation(mutationOptions),
    onSuccess: () => {
      void queryClient.invalidateQueries({
        queryKey: getBootSourcesV1BootassetSourcesGetQueryKey(),
      });

      void queryClient.invalidateQueries({
        queryKey: getBootSourcesV1BootassetSourcesGetInfiniteQueryKey(),
      });
    },
  });
};

export const useUpdateImageSource = (mutationOptions?: Options<PatchBootSourceV1BootassetSourcesIdPatchData>) => {
  const queryClient = useQueryClient();
  return useMutation({
    ...patchBootSourceV1BootassetSourcesIdPatchMutation(mutationOptions),
    onSuccess: (variables) => {
      void queryClient.invalidateQueries({
        queryKey: getBootSourcesV1BootassetSourcesGetQueryKey(),
      });

      void queryClient.invalidateQueries({
        queryKey: getBootSourcesV1BootassetSourcesGetInfiniteQueryKey(),
      });

      if (variables?.id) {
        void queryClient.invalidateQueries({
          queryKey: getBootSourceByIdV1BootassetSourcesIdGetQueryKey({ path: { id: variables.id } }),
        });
      }
    },
  });
};

export const useDeleteImageSource = (
  mutationOptions?: Partial<Options<DeleteBootSourceV1BootassetSourcesIdDeleteData>>,
) => {
  const queryClient = useQueryClient();
  return useMutation({
    ...deleteBootSourceV1BootassetSourcesIdDeleteMutation(mutationOptions),
    onSuccess: () => {
      void queryClient.invalidateQueries({
        queryKey: getBootSourcesV1BootassetSourcesGetQueryKey(),
      });

      void queryClient.invalidateQueries({
        queryKey: getBootSourcesV1BootassetSourcesGetInfiniteQueryKey(),
      });
    },
  });
};
