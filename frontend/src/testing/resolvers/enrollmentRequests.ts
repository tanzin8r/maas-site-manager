import { http, HttpResponse } from "msw";

import type { PendingSite, PendingSitesPostRequest } from "@/api";
import { enrollmentRequestFactory } from "@/mocks/factories";
import { apiUrls } from "@/utils/test-urls";

const mockEnrollmentRequests = enrollmentRequestFactory.buildList(155);

const enrollmentRequestsResolvers = {
  listEnrollmentRequests: {
    resolved: false,
    handler: (data: PendingSite[] = mockEnrollmentRequests) => {
      return http.get(apiUrls.enrollmentRequests, async ({ request }) => {
        const searchParams = new URL(request.url).searchParams;
        const page = Number(searchParams.get("page"));
        const size = Number(searchParams.get("size"));
        const itemsPage = data.slice((page - 1) * size, page * size);
        const response = {
          items: itemsPage,
          page,
          total: data.length,
        };
        enrollmentRequestsResolvers.listEnrollmentRequests.resolved = true;
        return HttpResponse.json(response);
      });
    },
  },
  postEnrollmentRequests: {
    resolved: false,
    handler: () => {
      return http.post(apiUrls.enrollmentRequests, async ({ request }) => {
        const { ids, accept } = (await request.json()) as PendingSitesPostRequest;
        enrollmentRequestsResolvers.postEnrollmentRequests.resolved = true;
        if (ids && typeof accept === "boolean") {
          return new HttpResponse(null, { status: 204 });
        } else {
          return new HttpResponse(null, { status: 400 });
        }
      });
    },
  },
};

export { enrollmentRequestsResolvers };
