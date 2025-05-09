import { http, HttpResponse } from "msw";

import type { SortDirection } from "@/api/handlers";
import type {
  BootSource,
  BootSourcesPostRequest,
  BootSourcesPostResponse,
  GetBootSourcesV1BootassetSourcesGetResponse,
} from "@/apiclient";
import { imageSourceFactory } from "@/mocks/factories";
import { apiUrls } from "@/utils/test-urls";

type BootSourcesSortKey = keyof Pick<BootSource, "id" | "url" | "priority" | "sync_interval">;

const mockImageSources = imageSourceFactory.buildList(10);

const imageSourceResolvers = {
  listImageSources: {
    resolved: false,
    handler: (data: BootSource[] = mockImageSources) => {
      return http.get(apiUrls.imageSources, async ({ request }) => {
        const searchParams = new URL(request.url).searchParams;
        const page = Number(searchParams.get("page")) || 1;
        const size = Number(searchParams.get("size")) || 10;
        const sortBy = searchParams.get("sortBy");
        if (sortBy) {
          const [field, order] = sortBy.split("-") as [BootSourcesSortKey, SortDirection];
          data.sort((a, b) => {
            if (a[field] < b[field]) {
              return order === "asc" ? -1 : 1;
            } else if (a[field] > b[field]) {
              return order === "asc" ? 1 : -1;
            }
            return a.id - b.id;
          });
        }
        const start = (page - 1) * size;
        const end = page * size;
        const itemsPage = data.slice(start, end);
        const response: GetBootSourcesV1BootassetSourcesGetResponse = {
          items: itemsPage,
          page,
          total: data.length,
          size,
        };
        imageSourceResolvers.listImageSources.resolved = true;
        return HttpResponse.json(response);
      });
    },
  },
  getImageSource: {
    resolved: false,
    handler: (data: BootSource[] = mockImageSources) => {
      return http.get(`${apiUrls.imageSources}/:id`, ({ params }) => {
        const id = parseInt(params.id as string, 10);
        const imageSource = data.find((imageSource) => imageSource.id === id);
        imageSourceResolvers.getImageSource.resolved = true;
        return HttpResponse.json(imageSource);
      });
    },
  },
  createImageSource: {
    resolved: false,
    handler: () => {
      return http.post(apiUrls.imageSources, async ({ request }) => {
        const { url, keyring, priority, sync_interval } = (await request.json()) as BootSourcesPostRequest;
        const newImageSource = imageSourceFactory.build({
          url,
          keyring,
          priority,
          sync_interval,
        }) as BootSourcesPostResponse;
        imageSourceResolvers.createImageSource.resolved = true;
        return new HttpResponse(JSON.stringify(newImageSource), {
          status: 201,
          headers: { "Content-Type": "application/json" },
        });
      });
    },
  },
  updateImageSource: {
    resolved: false,
    handler: () => {
      return http.patch(`${apiUrls.imageSources}/:id`, async () => {
        imageSourceResolvers.updateImageSource.resolved = true;
        return new HttpResponse(null, { status: 200 });
      });
    },
  },
  deleteImageSource: {
    resolved: false,
    handler: () => {
      return http.delete(`${apiUrls.imageSources}/:id`, async () => {
        imageSourceResolvers.deleteImageSource.resolved = true;
        return new HttpResponse(null, { status: 204 });
      });
    },
  },
};

export { imageSourceResolvers, mockImageSources };
