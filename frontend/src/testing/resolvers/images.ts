import { http, HttpResponse } from "msw";

import type { Image, UpstreamImage, UpstreamImageSource } from "@/api";
import { type ImagesSortKey, type SortDirection } from "@/api/handlers";
import { imageFactory, upstreamImageSourceFactory } from "@/mocks/factories";
import { apiUrls } from "@/utils/test-urls";

const mockImages = imageFactory.buildList(155);
const imagesResolvers = {
  listImages: {
    resolved: false,
    handler: (data: Image[] = mockImages) => {
      return http.get(apiUrls.bootAssets, async ({ request }) => {
        const searchParams = new URL(request.url).searchParams;
        const page = Number(searchParams.get("page"));
        const size = Number(searchParams.get("size"));
        const sortBy = searchParams.get("sortBy");
        if (sortBy) {
          const [field, order] = sortBy.split("-") as [ImagesSortKey, SortDirection];
          data.sort((a, b) => {
            if (a.codename < b.codename) {
              return -1;
            } else if (a.codename > b.codename) {
              return 1;
            } else {
              if (a[field] < b[field]) {
                return order === "asc" ? -1 : 1;
              } else if (a[field] > b[field]) {
                return order === "asc" ? 1 : -1;
              } else {
                return 0;
              }
            }
          });
        }

        const start = (page - 1) * size;
        const end = page * size;
        const itemsPage = data.slice(start, end);

        const response = {
          items: itemsPage,
          page,
          total: data.length,
          size,
        };

        imagesResolvers.listImages.resolved = true;
        return HttpResponse.json(response);
      });
    },
  },
  listUpstreamImages: {
    resolved: false,
    handler: (data: UpstreamImage[] = mockImages) => {
      return http.get(apiUrls.upstreamImages, ({ request }) => {
        const searchParams = new URL(request.url).searchParams;
        const page = Number(searchParams.get("page"));
        const size = Number(searchParams.get("size"));
        const items_page = data.slice((page - 1) * size, page * size);
        const response = {
          items: items_page,
          page,
          total: data.length,
          size,
        };
        imagesResolvers.listUpstreamImages.resolved = true;
        return HttpResponse.json(response);
      });
    },
  },
  getImageSource: {
    resolved: false,
    handler: (data: Omit<UpstreamImageSource, "credentials"> = upstreamImageSourceFactory.build()) => {
      return http.get(apiUrls.upstreamImageSource, () => {
        const response = data;
        imagesResolvers.getImageSource.resolved = true;
        return HttpResponse.json(response);
      });
    },
  },
  updateUpstreamImageSource: {
    resolved: false,
    handler: () => {
      return http.patch(apiUrls.upstreamImageSource, async () => {
        imagesResolvers.updateUpstreamImageSource.resolved = true;
        return new HttpResponse(null, { status: 200 });
      });
    },
  },
  selectUpstreamImages: {
    resolved: false,
    handler: () => {
      return http.post(apiUrls.upstreamImages, async () => {
        imagesResolvers.selectUpstreamImages.resolved = true;
        return new HttpResponse(null, { status: 200 });
      });
    },
  },
  deleteImages: {
    resolved: false,
    handler: () => {
      return http.delete(`${apiUrls.bootAssets}/:id`, async ({ request }) => {
        imagesResolvers.deleteImages.resolved = true;
        const ids = await request.json();

        if (Array.isArray(ids) && ids.length > 0) {
          return new HttpResponse(null, { status: 204 });
        }
        return new HttpResponse(null, { status: 400 });
      });
    },
  },
  uploadImage: {
    resolved: false,
    handler: () => {
      return http.post(apiUrls.images, async () => {
        imagesResolvers.uploadImage.resolved = true;
        return new HttpResponse(null, { status: 201 });
      });
    },
  },
};

export { imagesResolvers };
