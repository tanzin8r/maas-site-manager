import { setupWorker } from "msw";

import {
  postLogin,
  getSites,
  getTokens,
  getUsers,
  getEnrollmentRequests,
  postEnrollmentRequests,
  postTokens,
  deleteTokens,
  getCurrentUser,
  updateUser,
  addUser,
} from "./resolvers";

export const worker = setupWorker(
  postLogin,
  getSites,
  getUsers,
  postTokens,
  getEnrollmentRequests,
  postEnrollmentRequests,
  getTokens,
  deleteTokens,
  getCurrentUser,
  updateUser,
  addUser,
);
