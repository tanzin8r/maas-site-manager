import { setupWorker } from "msw";

import {
  postLogin,
  getSites,
  getTokens,
  getEnrollmentRequests,
  patchEnrollmentRequests,
  postTokens,
  deleteTokens,
} from "./resolvers";

export const worker = setupWorker(
  postLogin,
  getSites,
  postTokens,
  getEnrollmentRequests,
  patchEnrollmentRequests,
  getTokens,
  deleteTokens,
);
