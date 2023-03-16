// src/mocks/browser.js
import { rest } from "msw";
import { setupServer } from "msw/node";

import { createMockSitesResolver } from "./resolvers";

import urls from "@/api/urls";

const createMockGetServer = (endpoint: string, resolver: ReturnType<typeof createMockSitesResolver>) =>
  setupServer(rest.get(endpoint, resolver));
const createMockPostServer = (endpoint: string, resolver: ReturnType<typeof createMockSitesResolver>) =>
  setupServer(rest.post(endpoint, resolver));

const mockSitesServer = createMockGetServer(urls.sites, createMockSitesResolver());
const mockPostTokensServer = createMockPostServer(urls.tokens, createMockSitesResolver());

export { createMockGetServer, createMockPostServer, mockSitesServer, mockPostTokensServer };
