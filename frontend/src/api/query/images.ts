import type { Options } from "@hey-api/client-axios";
import { useMutation, useQueryClient } from "@tanstack/react-query";

import { type PostImagesV1ImagesPostData } from "@/apiclient";
import {
  getBootAssetsV1BootassetsGetQueryKey,
  postImagesV1ImagesPostMutation,
} from "@/apiclient/@tanstack/react-query.gen";

export const useUploadCustomImage = (mutationOptions?: Omit<Options<PostImagesV1ImagesPostData>, "body">) => {
  const queryClient = useQueryClient();

  return useMutation({
    ...postImagesV1ImagesPostMutation(mutationOptions),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: getBootAssetsV1BootassetsGetQueryKey() });
    },
  });
};
