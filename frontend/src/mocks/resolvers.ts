import { rest } from "msw";
import type { RestRequest, restContext, ResponseResolver } from "msw";

import { siteFactory, tokenFactory, enrollmentRequestFactory, accessTokenFactory } from "./factories";

import type { GetSitesQueryParams, PostTokensData } from "@/api/handlers";
import urls from "@/api/urls";
import { isDev } from "@/constants";

export const mockResponseDelay = isDev ? 0 : 0;
export const sitesList = siteFactory.buildList(155);
export const tokensList = tokenFactory.buildList(150);
export const enrollmentRequestsList = [
  enrollmentRequestFactory.build({ created: undefined }),
  ...enrollmentRequestFactory.buildList(100),
];
const accessToken = accessTokenFactory.build();

export const createMockLoginResolver =
  (): ResponseResolver<RestRequest<any, any>, typeof restContext> => async (req, res, ctx) => {
    const { username, password } = await req.body;
    if (username === "admin@example.com" && password === "admin") {
      return res(ctx.json(accessToken));
    }
    return res(
      ctx.status(401),
      ctx.set("WWW-Authenticate", "Bearer"),
      ctx.json({ detail: "Incorrect username or password" }),
    );
  };

type SitesResponseResolver = ResponseResolver<RestRequest<never, GetSitesQueryParams>, typeof restContext>;
export const createMockSitesResolver =
  (sites = sitesList): SitesResponseResolver =>
  (req, res, ctx) => {
    const searchParams = new URLSearchParams(req.url.search);
    const page = Number(searchParams.get("page"));
    const size = Number(searchParams.get("size"));
    const itemsPage = sites.slice((page - 1) * size, page * size);
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
  const { amount, duration } = await req.json();
  if (amount && duration) {
    items = Array(amount).fill(tokenFactory.build());
  } else {
    return res(ctx.status(400));
  }
  const response = {
    items,
  };

  return res(ctx.json(response));
};

export const createMockGetTokensResolver =
  (tokens = tokensList): TokensResponseResolver =>
  (req, res, ctx) => {
    const searchParams = new URLSearchParams(req.url.search);
    const page = Number(searchParams.get("page"));
    const size = Number(searchParams.get("size"));
    const itemsPage = tokens.slice((page - 1) * size, page * size);

    const response = {
      items: itemsPage,
      page,
      total: tokens.length,
    };

    return res(ctx.json(response));
  };

type DeleteTokensResponseResolver = ResponseResolver<RestRequest, typeof restContext>;
export const createMockDeleteTokensResolver = (): DeleteTokensResponseResolver => async (req, res, ctx) => {
  const ids = req.body;
  if (Array.isArray(ids) && ids.length > 0) {
    return res(ctx.status(204));
  }
  return res(ctx.status(400));
};

export const createMockGetEnrollmentRequestsResolver =
  (enrollmentRequests = enrollmentRequestsList): TokensResponseResolver =>
  (req, res, ctx) => {
    const searchParams = new URLSearchParams(req.url.search);
    const page = Number(searchParams.get("page"));
    const size = Number(searchParams.get("size"));
    const itemsPage = enrollmentRequests.slice((page - 1) * size, page * size);

    const response = {
      items: itemsPage,
      page,
      total: enrollmentRequests.length,
    };

    return res(ctx.json(response));
  };

type PostEnrollmentRequestsResponseResolver = ResponseResolver<RestRequest<PostTokensData>, typeof restContext>;
export const createMockPostEnrollmentRequestsResolver =
  (): PostEnrollmentRequestsResponseResolver => async (req, res, ctx) => {
    const { ids, accept } = await req.json();
    if (ids && typeof accept === "boolean") {
      return res(ctx.status(204));
    } else {
      return res(ctx.status(400));
    }
  };

export const postLogin = rest.post(urls.login, createMockLoginResolver());
export const getSites = rest.get(urls.sites, createMockSitesResolver());
export const postTokens = rest.post(urls.tokens, createMockTokensResolver());
export const getTokens = rest.get(urls.tokens, createMockGetTokensResolver());
export const deleteTokens = rest.delete(urls.tokens, createMockDeleteTokensResolver());
export const getEnrollmentRequests = rest.get(urls.enrollmentRequests, createMockGetEnrollmentRequestsResolver());
export const postEnrollmentRequests = rest.post(urls.enrollmentRequests, createMockPostEnrollmentRequestsResolver());
export const allResolvers = [getSites, postTokens, getTokens, getEnrollmentRequests, postEnrollmentRequests];
