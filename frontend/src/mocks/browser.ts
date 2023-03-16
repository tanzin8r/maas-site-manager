import { setupWorker } from "msw";

import { getSites, postTokens } from "./resolvers";

export const worker = setupWorker(getSites, postTokens);
