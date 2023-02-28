// src/mocks/browser.js
import { setupWorker, rest } from "msw";

import { sites } from "./factories";

const worker = setupWorker(
  rest.get("/api/sites", (_req, res, ctx) => {
    return res(ctx.json(sites));
  }),
);

worker.start();
