import type { RestRequest, restContext, ResponseResolver } from "msw";

import type { GetSitesQueryParams } from "../api/handlers";

import { siteFactory } from "./factories";

export const sitesList = siteFactory.buildList(155);

type SitesResponseResolver = ResponseResolver<RestRequest<never, GetSitesQueryParams>, typeof restContext>;
export const createMockSitesResolver =
  (sites = sitesList): SitesResponseResolver =>
  (req, res, ctx) => {
    const searchParams = new URLSearchParams(req.url.search);
    const page = Number(searchParams.get("page"));
    const size = Number(searchParams.get("size"));
    const itemsPage = sites.slice(page * Number(size), (page + 1) * size);
    const response = {
      items: itemsPage,
      page,
      total: sites.length,
    };

    return res(ctx.json(response));
  };
