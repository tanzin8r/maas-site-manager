import * as React from "react";

import * as Sentry from "@sentry/browser";
import * as ReactDOM from "react-dom/client";

import packageInfo from "../package.json";

import App from "./App";
import { useMockData } from "./constants";

/* c8 ignore next 4 */
if (useMockData) {
  const { worker } = await import("./mocks/browser");
  await worker.start();
}

const environment = process.env.NODE_ENV;
const version = packageInfo.version;
const release = import.meta.env.VITE_APP_VERSION;
if (environment !== "test") {
  // eslint-disable-next-line no-console
  console.log(`%cMAAS Site Manager \n${version} ${release}\n${environment}`, "color: #e95420; font-weight: bold;");
}

// https://sentry.is.canonical.com/canonical/maas-site-manager/
Sentry.init({
  dsn: import.meta.env.VITE_SENTRY_DSN,
  environment,
  release,
  beforeSend: (event) => ({
    ...event,
    // send just the pathname of the current page excluding the origin
    // this allows for grouping of errors by route
    tags: { ...event.tags, url: window.location.pathname, version },
  }),
});

ReactDOM.createRoot(document.getElementById("root") as HTMLElement).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
