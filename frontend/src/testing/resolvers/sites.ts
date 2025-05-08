import { http, HttpResponse } from "msw";

import type { SitesSortKey, SortDirection } from "@/api/handlers";
import type { GetV1SitesGetData, Site, SitesGetResponse } from "@/apiclient";
import { siteFactory } from "@/mocks/factories";
import { apiUrls } from "@/utils/test-urls";

const mockSites = siteFactory.buildList(155);
const sitesResolvers = {
  listSites: {
    resolved: false,
    handler: (data: Site[] = mockSites) => {
      return http.get(apiUrls.sites, ({ request }) => {
        const searchParams = new URL(request.url).searchParams;
        const page = Number(searchParams.get("page"));
        const size = Number(searchParams.get("size"));
        const queryText = searchParams.get("q")?.replace("+", " ");

        // sort items
        const items = [...data];

        // this filters for name only, backend filters for multiple parameters
        const filteredItems = queryText
          ? items.filter((site) => site.name.toLowerCase().includes(queryText?.toLowerCase()))
          : items;

        const sortBy = searchParams.get("sortBy") as NonNullable<GetV1SitesGetData["query"]>["sort_by"];
        if (sortBy) {
          const [field, order] = sortBy.split("-") as [SitesSortKey, SortDirection];
          filteredItems.sort((a, b) => {
            if (order === "asc") {
              return a[field] > b[field] ? 1 : -1;
            }
            return a[field] < b[field] ? 1 : -1;
          });
        }
        const itemsPage = filteredItems.slice((page - 1) * size, page * size);

        const response: SitesGetResponse = {
          items: itemsPage,
          page,
          total: data.length,
          size,
        };
        sitesResolvers.listSites.resolved = true;
        return HttpResponse.json(response);
      });
    },
  },
  sitesCoordinates: {
    resolved: false,
    handler: (data: Site[] = mockSites) => {
      return http.get(apiUrls.sitesCoordinates, () => {
        const response = data.map(({ id, coordinates }) => ({ id, coordinates }));
        return HttpResponse.json(response);
      });
    },
  },
  getSite: {
    resolved: false,
    handler: (data: Site[] = mockSites) => {
      return http.get(`${apiUrls.sites}/:id`, ({ params }) => {
        const id = Number(params.id);
        const site = data.find((site) => site.id === id) as Site;
        return HttpResponse.json({ ...site });
      });
    },
  },
  deleteSites: {
    resolved: false,
    handler: () => {
      return http.delete(apiUrls.sites, () => {
        return new HttpResponse(null, { status: 204 });
      });
    },
  },
  updateSites: {
    resolved: false,
    handler: () => {
      return http.put(apiUrls.sites, async ({ request }) => {
        const site = await { ...request.json() };
        return new HttpResponse(JSON.stringify(site), {
          status: 200,
          headers: { "Content-Type": "application/json" },
        });
      });
    },
  },
};

export { sitesResolvers };
