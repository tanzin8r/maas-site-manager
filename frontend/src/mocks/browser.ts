import { setupWorker, rest } from "msw";

import urls from "../api/urls";

import { sites } from "./factories";

export const worker = setupWorker(
  rest.get(urls.sites, (_req, res, ctx) => {
    return res(ctx.json(sites()));
  }),
);
