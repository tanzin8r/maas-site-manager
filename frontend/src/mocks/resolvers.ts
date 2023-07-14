import { rest } from "msw";
import type { RestRequest, restContext, ResponseResolver } from "msw";

import { siteFactory, tokenFactory, enrollmentRequestFactory, accessTokenFactory, userFactory } from "./factories";

import type {
  GetSitesQueryParams,
  GetUsersQueryParams,
  PostTokensData,
  SortDirection,
  SitesSortKey,
  UserSortKey,
} from "@/api/handlers";
import type { User } from "@/api/types";
import urls from "@/api/urls";
import { isDev } from "@/constants";

export const mockResponseDelay = isDev ? 0 : 0;
export const sitesList = siteFactory.buildList(155);
export const tokensList = tokenFactory.buildList(150);
export const usersList = userFactory.buildList(20);
export const enrollmentRequestsList = [
  enrollmentRequestFactory.build({ created: undefined }),
  ...enrollmentRequestFactory.buildList(100),
];
const accessToken = accessTokenFactory.build();

export const createMockLoginResolver =
  (): ResponseResolver<RestRequest<any, any>, typeof restContext> => async (req, res, ctx) => {
    const { email, password } = await req.body;
    if (email === "admin@example.com" && password === "admin") {
      return res(ctx.json(accessToken));
    }
    return res(
      ctx.status(401),
      ctx.set("WWW-Authenticate", "Bearer"),
      ctx.json({ detail: "Incorrect email or password" }),
    );
  };

type SitesResponseResolver = ResponseResolver<RestRequest, typeof restContext>;
export const createMockSitesResolver =
  (sites = sitesList): SitesResponseResolver =>
  (req, res, ctx) => {
    const searchParams = new URLSearchParams(req.url.search);
    const page = Number(searchParams.get("page"));
    const size = Number(searchParams.get("size"));
    // sort items
    const items = [...sites];
    const sortBy = searchParams.get("sort_by") as GetSitesQueryParams["sort_by"];
    if (sortBy) {
      const [field, order] = sortBy.split("-") as [SitesSortKey, SortDirection];
      items.sort((a, b) => {
        if (order === "asc") {
          return a[field] > b[field] ? 1 : -1;
        }
        return a[field] < b[field] ? 1 : -1;
      });
    }
    const itemsPage = items.slice((page - 1) * size, page * size);

    const response = {
      items: itemsPage,
      page,
      total: sites.length,
    };

    return res(ctx.json(response));
  };

type TokensResponseResolver = ResponseResolver<RestRequest, typeof restContext>;
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

type UsersResponseResolver = ResponseResolver<RestRequest, typeof restContext>;
export const createMockGetUsersResolver =
  (users = usersList): UsersResponseResolver =>
  (req, res, ctx) => {
    const searchParams = new URLSearchParams(req.url.search);
    const page = Number(searchParams.get("page"));
    const size = Number(searchParams.get("size"));

    // sort items
    const items = [...users];
    const sortBy = searchParams.get("sort_by") as GetUsersQueryParams["sort_by"];
    if (sortBy) {
      const [field, order] = sortBy.split("-") as [UserSortKey, SortDirection];
      items.sort((a, b) => {
        if (order === "asc") {
          return a[field] > b[field] ? 1 : -1;
        }
        return a[field] < b[field] ? 1 : -1;
      });
    }

    const itemsPage = items.slice((page - 1) * size, page * size);

    const response = {
      items: itemsPage,
      page,
      total: users.length,
    };

    return res(ctx.json(response));
  };

type UserResponseResolver = ResponseResolver<RestRequest, typeof restContext>;
export const createMockGetUserResolver =
  (users = usersList): UserResponseResolver =>
  (req, res, ctx) => {
    const id = req.params.id;

    const user = users.find((user: User) => user.id === Number(id));
    return res(ctx.json(user));
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

type CurrentUserResponseResolver = ResponseResolver<RestRequest, typeof restContext>;
export const createMockCurrentUserResolver =
  (templateUser?: Partial<User>): CurrentUserResponseResolver =>
  async (req, res, ctx) => {
    const user = userFactory.build(
      templateUser ? templateUser : { username: "admin", full_name: "MAAS Admin", email: "admin@example.com" },
    );
    return res(ctx.status(200), ctx.json(user));
  };

type UpdateUserResponseResolver = ResponseResolver<RestRequest<User, { id: string }>, typeof restContext>;
export const createMockUpdateUserResolver = (): UpdateUserResponseResolver => async (req, res, ctx) => {
  const { full_name, username, email, is_admin } = req.body;
  const id = req.params.id;
  const user = { id: Number(id), full_name, username, email, is_admin };
  return res(ctx.status(200), ctx.json(user));
};

type AddUserResponseResolver = ResponseResolver<RestRequest<User>, typeof restContext>;
export const createMockAddUserResolver = (): AddUserResponseResolver => async (req, res, ctx) => {
  const { username, full_name, email, is_admin } = req.body;
  const newUser = userFactory.build({ username, full_name, email, is_admin });
  return res(ctx.status(201), ctx.json(newUser));
};

export const postLogin = rest.post(urls.login, createMockLoginResolver());
export const getSites = rest.get(urls.sites, createMockSitesResolver());
export const postTokens = rest.post(urls.tokens, createMockTokensResolver());
export const getTokens = rest.get(urls.tokens, createMockGetTokensResolver());
export const deleteTokens = rest.delete(urls.tokens, createMockDeleteTokensResolver());
export const getUsers = rest.get(urls.users, createMockGetUsersResolver());
export const getUser = rest.get(`${urls.users}/:id`, createMockGetUserResolver());
export const getEnrollmentRequests = rest.get(urls.enrollmentRequests, createMockGetEnrollmentRequestsResolver());
export const postEnrollmentRequests = rest.post(urls.enrollmentRequests, createMockPostEnrollmentRequestsResolver());
export const getCurrentUser = rest.get(urls.currentUser, createMockCurrentUserResolver());
export const updateUser = rest.patch(`${urls.users}/:id`, createMockUpdateUserResolver());
export const addUser = rest.post(urls.users, createMockAddUserResolver());
export const allResolvers = [
  getSites,
  postTokens,
  getTokens,
  getEnrollmentRequests,
  postEnrollmentRequests,
  getCurrentUser,
  updateUser,
  getUsers,
  addUser,
  getUser,
];
