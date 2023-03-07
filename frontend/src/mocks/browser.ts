import { setupWorker, rest } from "msw";

import urls from "../api/urls";

import { createMockSitesResolver } from "./resolvers";

export const worker = setupWorker(rest.get(urls.sites, createMockSitesResolver()));
