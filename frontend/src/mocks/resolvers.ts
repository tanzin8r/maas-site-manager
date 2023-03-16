import { rest } from "msw";
import type { RestRequest, restContext, ResponseResolver } from "msw";

import { siteFactory, tokenFactory } from "./factories";

import urls from "@/api/urls";
import type { GetSitesQueryParams, PostTokensData } from "api/handlers";

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

type TokensResponseResolver = ResponseResolver<RestRequest<PostTokensData>, typeof restContext>;
export const createMockTokensResolver = (): TokensResponseResolver => async (req, res, ctx) => {
  let items;
  const { amount, name, expires } = await req.json();
  if (amount && name && expires) {
    items = Array(amount).fill(tokenFactory.build({ name, expires }));
  }
  const response = {
    items,
  };

  return res(ctx.json(response));
};

export const getSites = rest.get(urls.sites, createMockSitesResolver());
export const postTokens = rest.post(urls.tokens, createMockTokensResolver());
