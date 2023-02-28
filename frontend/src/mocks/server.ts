// src/mocks/browser.js
import { setupServer } from "msw/node";
import { rest } from "msw";
import { sites } from "./factories";
import urls from "../api/urls";

const createMockGetServer = (endpoint: string, response: object) =>
  setupServer(
    rest.get(endpoint, (_req, res, ctx) => {
      return res(ctx.json(response));
    })
  );

const mockSitesServer = createMockGetServer(urls.sites, sites());

export { createMockGetServer, mockSitesServer };
