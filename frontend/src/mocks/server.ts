// src/mocks/browser.js
import { rest } from "msw";
import { setupServer } from "msw/node";

import urls from "../api/urls";

import { createMockSitesResolver } from "./resolvers";

const createMockGetServer = (endpoint: string, resolver: ReturnType<typeof createMockSitesResolver>) =>
  setupServer(rest.get(endpoint, resolver));

const mockSitesServer = createMockGetServer(urls.sites, createMockSitesResolver());

export { createMockGetServer, mockSitesServer };
