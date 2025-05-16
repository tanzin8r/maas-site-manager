import type { Options } from "@hey-api/client-axios";
import type { UseQueryOptions } from "@tanstack/react-query";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import type { AxiosError } from "axios";

import type {
  PostPendingV1SitesPendingPostError,
  PostPendingV1SitesPendingPostResponse,
  GetPendingV1SitesPendingGetData,
  GetPendingV1SitesPendingGetError,
  GetPendingV1SitesPendingGetResponse,
  PostPendingV1SitesPendingPostData,
} from "@/apiclient";
import {
  getPendingV1SitesPendingGetOptions,
  getPendingV1SitesPendingGetQueryKey,
  postPendingV1SitesPendingPostMutation,
} from "@/apiclient/@tanstack/react-query.gen";

export const useEnrollmentRequests = (options?: Options<GetPendingV1SitesPendingGetData>) => {
  return useQuery(
    getPendingV1SitesPendingGetOptions(options) as UseQueryOptions<
      GetPendingV1SitesPendingGetData,
      GetPendingV1SitesPendingGetError,
      GetPendingV1SitesPendingGetResponse
    >,
  );
};

export type UseEnrollmentRequestsResult = ReturnType<typeof useEnrollmentRequests>;

export const useEnrollmentRequestsAction = (mutationOptions?: Options<PostPendingV1SitesPendingPostData>) => {
  const queryClient = useQueryClient();

  return useMutation<
    PostPendingV1SitesPendingPostResponse,
    AxiosError<PostPendingV1SitesPendingPostError>,
    Options<PostPendingV1SitesPendingPostData>
  >({
    ...postPendingV1SitesPendingPostMutation(mutationOptions),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: getPendingV1SitesPendingGetQueryKey() });
    },
  });
};
