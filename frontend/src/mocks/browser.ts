import { setupWorker } from "msw";

import {
  postLogin,
  getSites,
  getTokens,
  getEnrollmentRequests,
  patchEnrollmentRequests,
  postTokens,
} from "./resolvers";

export const worker = setupWorker(
  postLogin,
  getSites,
  postTokens,
  getEnrollmentRequests,
  patchEnrollmentRequests,
  getTokens,
);
