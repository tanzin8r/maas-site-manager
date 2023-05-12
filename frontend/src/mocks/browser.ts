import { setupWorker } from "msw";

import {
  postLogin,
  getSites,
  getTokens,
  getEnrollmentRequests,
  postEnrollmentRequests,
  postTokens,
  deleteTokens,
} from "./resolvers";

export const worker = setupWorker(
  postLogin,
  getSites,
  postTokens,
  getEnrollmentRequests,
  postEnrollmentRequests,
  getTokens,
  deleteTokens,
);
