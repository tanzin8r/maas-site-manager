import { rest } from "msw";
import type { RestRequest, restContext, ResponseResolver, DelayMode } from "msw";

import {
  upstreamImageSourceFactory,
  siteFactory,
  tokenFactory,
  enrollmentRequestFactory,
  accessTokenFactory,
  userFactory,
  imageFactory,
  upstreamImageFactory,
  settingsFactory,
} from "./factories";

import type {
  GetSitesQueryParams,
  SortDirection,
  SitesSortKey,
  UserSortKey,
  UpstreamImageSource,
  SelectUpstreamImagesPayload,
  ImagesSortKey,
} from "@/api/handlers";
import type { User } from "@/api/types";
import type { TokensPostResponse } from "@/api-client";
import type { Site } from "@/api-client/models/Site";
import type { SitesGetResponse } from "@/api-client/models/SitesGetResponse";
import { isDev } from "@/constants";
import staticTileImage from "@/mocks/assets/static-tile.png";
import { apiUrls } from "@/utils/test-urls";

export const mockResponseDelay: DelayMode | number = isDev ? "real" : 0;
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
    const { username, password } = await req.body;
    if (username === "admin@example.com" && password === "admin") {
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
    const sortBy = searchParams.get("sortBy") as GetSitesQueryParams["sortBy"];
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

    const response: SitesGetResponse = {
      items: itemsPage,
      page,
      total: sites.length,
      size,
    };

    return res(ctx.json(response));
  };

export const createMockSitesCoordinatesResolver =
  (sites = sitesList): SitesResponseResolver =>
  (req, res, ctx) => {
    const response = sites.map(({ id, coordinates }) => ({ id, coordinates }));

    return res(ctx.json(response));
  };

export const createMockSiteResolver =
  (sites = sitesList): ResponseResolver<RestRequest, typeof restContext> =>
  (req, res, ctx) => {
    const id = Number(req.params.id);

    const site = sites.find((site) => site.id === id) as Site;
    return res(ctx.json({ ...site }));
  };

type DeleteSitesResponseResolver = ResponseResolver<RestRequest, typeof restContext>;
export const createMockDeleteSitesResolver = (): DeleteSitesResponseResolver => async (req, res, ctx) => {
  const ids = req.json();

  if (Array.isArray(ids) && ids.length > 0) {
    return res(ctx.status(204));
  } else {
    return res(ctx.status(400));
  }
};

type DeleteSiteResponseResolver = ResponseResolver<RestRequest, typeof restContext>;
export const createMockDeleteSiteResolver = (): DeleteSiteResponseResolver => async (_req, res, ctx) => {
  return res(ctx.status(204));
};

type UpdateSiteResponseResolver = ResponseResolver<RestRequest<Site, { id: string }>, typeof restContext>;
export const createMockUpdateSiteResolver = (): UpdateSiteResponseResolver => async (req, res, ctx) => {
  const site = { ...req.body };
  return res(ctx.status(200), ctx.json(site));
};

type TokensResponseResolver = ResponseResolver<RestRequest, typeof restContext>;
export const createMockTokensResolver = (): TokensResponseResolver => async (req, res, ctx) => {
  let tokens;
  const { count, duration } = await req.json();
  if (count && duration) {
    tokens = Array(count).fill(tokenFactory.build());
  } else {
    return res(ctx.status(400));
  }
  const response: TokensPostResponse = { items: tokens };

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
  const ids = req.json();

  if (Array.isArray(ids) && ids.length > 0) {
    return res(ctx.status(204));
  }
  return res(ctx.status(400));
};

type DeleteTokenResponseResolver = ResponseResolver<RestRequest, typeof restContext>;
export const createMockDeleteTokenResolver = (): DeleteTokenResponseResolver => async (_req, res, ctx) => {
  return res(ctx.status(204));
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
    const sortBy = searchParams.get("sortBy");
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

type PostEnrollmentRequestsResponseResolver = ResponseResolver<RestRequest, typeof restContext>;
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

type DeleteUserResponseResolver = ResponseResolver<RestRequest<{ id: string }>, typeof restContext>;
export const createMockDeleteUserResolver = (): DeleteUserResponseResolver => async (req, res, ctx) => {
  const id = req.params.id;
  if (Number(id) === 1) {
    return res(ctx.status(400));
  }
  return res(ctx.status(200));
};

export const postLogin = rest.post(apiUrls.login, createMockLoginResolver());
export const getSites = rest.get(apiUrls.sites, createMockSitesResolver());
export const getSitesCoordinates = rest.get(apiUrls.sitesCoordinates, createMockSitesCoordinatesResolver());
export const getSite = rest.get(`${apiUrls.sites}/:id`, createMockSiteResolver());
export const deleteSites = rest.delete(apiUrls.sites, createMockDeleteSitesResolver());
export const deleteSite = rest.delete(`${apiUrls.sites}/:id`, createMockDeleteSiteResolver());
export const updateSite = rest.patch(`${apiUrls.sites}/:id`, createMockUpdateSiteResolver());
export const postTokens = rest.post(apiUrls.tokens, createMockTokensResolver());
export const getTokens = rest.get(apiUrls.tokens, createMockGetTokensResolver());
export const deleteTokens = rest.delete(apiUrls.tokens, createMockDeleteTokensResolver());
export const deleteToken = rest.delete(`${apiUrls.tokens}/:id`, createMockDeleteTokenResolver());
export const getUsers = rest.get(apiUrls.users, createMockGetUsersResolver());
export const getUser = rest.get(`${apiUrls.users}/:id`, createMockGetUserResolver());
export const getEnrollmentRequests = rest.get(apiUrls.enrollmentRequests, createMockGetEnrollmentRequestsResolver());
export const postEnrollmentRequests = rest.post(apiUrls.enrollmentRequests, createMockPostEnrollmentRequestsResolver());
export const getCurrentUser = rest.get(apiUrls.currentUser, createMockCurrentUserResolver());
export const updateUser = rest.patch(`${apiUrls.users}/:id`, createMockUpdateUserResolver());
export const addUser = rest.post(apiUrls.users, createMockAddUserResolver());
export const deleteUser = rest.delete(`${apiUrls.users}/:id`, createMockDeleteUserResolver());
export const tileHandler = rest.get(/.*\.(?:png|jpg|jpeg|bmp)$/, async (req, res, ctx) => {
  if (req.url.host.includes("tile.openstreetmap.org")) {
    const image = await fetch(staticTileImage).then((res) => res.arrayBuffer());
    return res(ctx.status(200), ctx.set("Content-Type", "image/png"), ctx.body(image));
  }
});

export const getTokensExport = rest.get(apiUrls.tokensExport, async (_req, res, ctx) => {
  const csv = `id,value,expired,created
9,0e846493-fde9-4d15-844c-2ca0341d1e84,2024-01-01 00:00:00,2023-02-28 00:00:00
10,e15a7d3c-9df8-40c7-b81b-ed4796e777bc,2024-01-01 00:00:00,2023-02-28 00:00:00
11,87a62d9a-7645-43b5-9dd4-eaf53e768c4a,2024-01-01 00:00:00,2023-02-28 00:00:00`;

  return res(ctx.status(200), ctx.set("Content-Type", "text/csv"), ctx.body(csv));
});

type ImagesResponseResolver = ResponseResolver<RestRequest, typeof restContext>;
export const createMockImagesResolver =
  (images: ReturnType<typeof imageFactory.buildList>): ImagesResponseResolver =>
  (req, res, ctx) => {
    const searchParams = new URLSearchParams(req.url.search);
    const page = Number(searchParams.get("page"));
    const size = Number(searchParams.get("size"));
    const sortBy = searchParams.get("sortBy");
    if (sortBy) {
      const [field, order] = sortBy.split("-") as [ImagesSortKey, SortDirection];
      images.sort((a, b) => {
        if (a.name < b.name) {
          return -1;
        } else if (a.name > b.name) {
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
    const itemsPage = images.slice(start, end);

    const response = {
      items: itemsPage,
      page,
      total: images.length,
      size,
    };

    const delay = isDev ? 500 : 0;
    return res(ctx.delay(delay), ctx.status(200), ctx.json(response));
  };

const imagesList = imageFactory.buildList(25);
export const getImages = rest.get(apiUrls.images, createMockImagesResolver(imagesList));

type UpstreamImagesResponseResolver = ResponseResolver<RestRequest, typeof restContext>;
export const createMockUpstreamImagesResolver =
  (upstreamImages: ReturnType<typeof upstreamImageFactory.buildList>): UpstreamImagesResponseResolver =>
  (req, res, ctx) => {
    const searchParams = new URLSearchParams(req.url.search);
    const page = Number(searchParams.get("page"));
    const size = Number(searchParams.get("size"));
    const items_page = upstreamImages.slice((page - 1) * size, page * size);

    const response = {
      items: items_page,
      page,
      total: upstreamImages.length,
      size,
    };

    return res(ctx.status(200), ctx.json(response));
  };

export const getUpstreamImages = rest.get(
  apiUrls.upstreamImages,
  createMockUpstreamImagesResolver(upstreamImageFactory.buildList(10)),
);

type UpstreamImageSourceResponseResolver = ResponseResolver<RestRequest, typeof restContext>;
export const createMockUpstreamImageSourceResolver =
  (upstreamImageSource: ReturnType<typeof upstreamImageSourceFactory.build>): UpstreamImageSourceResponseResolver =>
  (_req, res, ctx) => {
    const response = upstreamImageSource;

    return res(ctx.status(200), ctx.json(response));
  };

export const getUpstreamImageSource = rest.get(
  apiUrls.upstreamImageSource,
  createMockUpstreamImageSourceResolver(upstreamImageSourceFactory.build()),
);

type UpdateUpstreamImageSourceResponseResolver = ResponseResolver<RestRequest<UpstreamImageSource>, typeof restContext>;
export const createMockUpdateUpstreamImageSourceResolver =
  (): UpdateUpstreamImageSourceResponseResolver => async (req, res, ctx) => {
    return res(ctx.status(200));
  };

export const updateUpstreamImageSource = rest.post(
  apiUrls.upstreamImageSource,
  createMockUpdateUpstreamImageSourceResolver(),
);

type SelectUpstreamImagesResponseResolver = ResponseResolver<
  RestRequest<SelectUpstreamImagesPayload[]>,
  typeof restContext
>;
export const createMockSelectUpstreamImagesResolver =
  (): SelectUpstreamImagesResponseResolver => async (req, res, ctx) => {
    return res(ctx.status(200));
  };

export const selectUpstreamImages = rest.post(apiUrls.upstreamImages, createMockSelectUpstreamImagesResolver());

type SettingsResponseResolver = ResponseResolver<RestRequest, typeof restContext>;

const defaultSettings = settingsFactory.build();
export const createMockGetSettingsResolver =
  (settings = defaultSettings): SettingsResponseResolver =>
  (req, res, ctx) => {
    return res(ctx.json(settings));
  };

export const createMockPatchSettingsResolver = (): SettingsResponseResolver => async (req, res, ctx) => {
  const body = await req.json();
  const updatedSettings = { ...defaultSettings, ...body };
  return res(ctx.json(updatedSettings));
};

type DeleteImageResponseResolver = ResponseResolver<RestRequest, typeof restContext>;
export const createMockDeleteImageResolver = (): DeleteImageResponseResolver => async (_req, res, ctx) => {
  return res(ctx.status(204));
};

const deleteImage = rest.delete(`${apiUrls.images}/:id`, createMockDeleteImageResolver());

type DeleteImagesResponseResolver = ResponseResolver<RestRequest, typeof restContext>;
export const createMockDeleteImagesResolver = (): DeleteImagesResponseResolver => async (req, res, ctx) => {
  const ids = req.json();

  if (Array.isArray(ids) && ids.length > 0) {
    return res(ctx.status(204));
  }
  return res(ctx.status(400));
};

const deleteImages = rest.delete(apiUrls.images, createMockDeleteImagesResolver());

const getSettings = rest.get(apiUrls.settings, createMockGetSettingsResolver());

const patchSettings = rest.patch(apiUrls.settings, createMockPatchSettingsResolver());

export const allResolvers = [
  postLogin,
  getSites,
  getSitesCoordinates,
  getEnrollmentRequests,
  getSite,
  deleteSites,
  deleteSite,
  updateSite,
  postTokens,
  deleteTokens,
  deleteToken,
  getTokens,
  postEnrollmentRequests,
  getCurrentUser,
  updateUser,
  getUsers,
  addUser,
  getUser,
  deleteUser,
  getTokensExport,
  getImages,
  getUpstreamImages,
  getUpstreamImageSource,
  updateUpstreamImageSource,
  selectUpstreamImages,
  getSettings,
  patchSettings,
  deleteImage,
  deleteImages,
  ...(import.meta.env.VITE_USE_MOCK_TILES === "true" ? [tileHandler] : []),
];
