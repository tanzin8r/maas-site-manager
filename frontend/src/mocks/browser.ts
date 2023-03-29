import { setupWorker } from "msw";

import { getSites, getTokens, getEnrollmentRequests, postTokens } from "./resolvers";

export const worker = setupWorker(getSites, postTokens, getEnrollmentRequests, getTokens);
