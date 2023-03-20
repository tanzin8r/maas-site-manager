import { setupWorker } from "msw";

import { getSites, getTokens, postTokens } from "./resolvers";

export const worker = setupWorker(getSites, postTokens, getTokens);
