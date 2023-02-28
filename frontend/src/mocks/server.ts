// src/mocks/browser.js
import { rest } from "msw";
import { setupServer } from "msw/node";

import urls from "../api/urls";

import { sites } from "./factories";

const createMockGetServer = (endpoint: string, response: object) =>
  setupServer(
    rest.get(endpoint, (_req, res, ctx) => {
      return res(ctx.json(response));
    }),
  );

const mockSitesServer = createMockGetServer(urls.sites, sites());

export { createMockGetServer, mockSitesServer };
