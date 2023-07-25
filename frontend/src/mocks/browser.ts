import { setupWorker } from "msw";

import {
  postLogin,
  getSites,
  getSite,
  getTokens,
  getUsers,
  getEnrollmentRequests,
  postEnrollmentRequests,
  postTokens,
  deleteTokens,
  getCurrentUser,
  updateUser,
  addUser,
  getUser,
  deleteUser,
} from "./resolvers";

export const worker = setupWorker(
  postLogin,
  getSites,
  getSite,
  getUsers,
  postTokens,
  getEnrollmentRequests,
  postEnrollmentRequests,
  getTokens,
  deleteTokens,
  getCurrentUser,
  updateUser,
  addUser,
  getUser,
  deleteUser,
);
