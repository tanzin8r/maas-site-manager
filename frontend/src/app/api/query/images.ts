import type { Options } from "@hey-api/client-axios";
import type { UseQueryOptions } from "@tanstack/react-query";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import type {
  DeleteImagesV1ImagesRemovePostData,
  GetImageSourcesV1ImageSourcesGetData,
  GetImageSourcesV1ImageSourcesGetError,
  GetImageSourcesV1ImageSourcesGetResponse,
  GetSelectableImagesV1SelectableImagesGetData,
  GetSelectableImagesV1SelectableImagesGetError,
  GetSelectableImagesV1SelectableImagesGetResponse,
  GetSelectedImagesV1SelectedImagesGetData,
  GetSelectedImagesV1SelectedImagesGetError,
  GetSelectedImagesV1SelectedImagesGetResponse,
  PostImagesV1ImagesPostData,
  RemoveSelectionsV1SelectedImagesRemovePostData,
  SelectImagesV1SelectableImagesSelectPostData,
} from "@/app/apiclient";
import {
  deleteImagesV1ImagesRemovePostMutation,
  getImageSourcesV1ImageSourcesGetOptions,
  getSelectableImagesV1SelectableImagesGetOptions,
  getSelectableImagesV1SelectableImagesGetQueryKey,
  getSelectedImagesV1SelectedImagesGetOptions,
  getSelectedImagesV1SelectedImagesGetQueryKey,
  postImagesV1ImagesPostMutation,
  removeSelectionsV1SelectedImagesRemovePostMutation,
  selectImagesV1SelectableImagesSelectPostMutation,
} from "@/app/apiclient/@tanstack/react-query.gen";

export const useSelectableImages = (options?: Options<GetSelectableImagesV1SelectableImagesGetData>) => {
  return useQuery(
    getSelectableImagesV1SelectableImagesGetOptions(options) as UseQueryOptions<
      GetSelectableImagesV1SelectableImagesGetData,
      GetSelectableImagesV1SelectableImagesGetError,
      GetSelectableImagesV1SelectableImagesGetResponse
    >,
  );
};

export const useSelectedImages = (options?: Options<GetSelectedImagesV1SelectedImagesGetData>) => {
  return useQuery(
    getSelectedImagesV1SelectedImagesGetOptions(options) as UseQueryOptions<
      GetSelectedImagesV1SelectedImagesGetData,
      GetSelectedImagesV1SelectedImagesGetError,
      GetSelectedImagesV1SelectedImagesGetResponse
    >,
  );
};

export const useGetAlternativesForImage = (
  options: Options<GetImageSourcesV1ImageSourcesGetData>,
  enabled: boolean,
) => {
  return useQuery({
    ...(getImageSourcesV1ImageSourcesGetOptions(options) as UseQueryOptions<
      GetImageSourcesV1ImageSourcesGetData,
      GetImageSourcesV1ImageSourcesGetError,
      GetImageSourcesV1ImageSourcesGetResponse
    >),
    enabled,
  });
};

export const useAddImagesToSelection = (
  mutationOptions?: Omit<Options<SelectImagesV1SelectableImagesSelectPostData>, "body">,
) => {
  const queryClient = useQueryClient();

  return useMutation({
    ...selectImagesV1SelectableImagesSelectPostMutation(mutationOptions),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: getSelectedImagesV1SelectedImagesGetQueryKey() });
      void queryClient.invalidateQueries({ queryKey: getSelectableImagesV1SelectableImagesGetQueryKey() });
    },
  });
};

export const useRemoveImagesFromSelection = (
  mutationOptions?: Omit<Options<RemoveSelectionsV1SelectedImagesRemovePostData>, "body">,
) => {
  const queryClient = useQueryClient();

  return useMutation({
    ...removeSelectionsV1SelectedImagesRemovePostMutation(mutationOptions),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: getSelectedImagesV1SelectedImagesGetQueryKey() });
      void queryClient.invalidateQueries({ queryKey: getSelectableImagesV1SelectableImagesGetQueryKey() });
    },
  });
};

export const useUploadCustomImage = (mutationOptions?: Omit<Options<PostImagesV1ImagesPostData>, "body">) => {
  const queryClient = useQueryClient();

  return useMutation({
    ...postImagesV1ImagesPostMutation(mutationOptions),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: getSelectedImagesV1SelectedImagesGetQueryKey() });
    },
  });
};

export const useDeleteCustomImage = (mutationOptions?: Options<DeleteImagesV1ImagesRemovePostData>) => {
  const queryClient = useQueryClient();

  return useMutation({
    ...deleteImagesV1ImagesRemovePostMutation(mutationOptions),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: getSelectedImagesV1SelectedImagesGetQueryKey() });
    },
  });
};
