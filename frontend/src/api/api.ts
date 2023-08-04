import * as Sentry from "@sentry/browser";
import axios from "axios";

import { baseURL } from "./config";

let authToken: string | null = null;
try {
  const persistedToken = localStorage.getItem("jwtToken");
  if (persistedToken) {
    authToken = String(JSON.parse(persistedToken));
  }
} catch (error) {
  Sentry.captureException(new Error("Failed to parse authToken", { cause: error }));
}

const api = axios.create({
  baseURL,
  headers: authToken
    ? {
        Authorization: `Bearer ${authToken}`,
      }
    : undefined,
});

export default api;
