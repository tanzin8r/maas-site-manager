import { http, HttpResponse } from "msw";

/**
 * Scenarios that override default MSW resolvers for testing purposes.
 *
 * To trigger a specific scenario, pass a URL search parameter with the key "scenario"
 * and the value corresponding to the desired scenario name.
 *
 * For example, to trigger the "sitesUnauthorized" scenario, append "?scenario=sitesUnauthorized"
 * to the URL.
 *
 * The available scenarios are defined the `scenarios` object below.
 */
const getApiUrl = (path: string) => `http://localhost:8000/api/v1${path}`;
const scenariosHandlers = {
  sitesUnauthorized: [
    http.get(getApiUrl("/sites"), () => {
      return new HttpResponse(JSON.stringify({ error: "Unaouthorized" }), {
        status: 401,
        headers: {
          "Content-Type": "application/json",
        },
      });
    }),
  ],
} as const;

export type ScenarioName = keyof typeof scenariosHandlers;

const scenarios = Object.keys(scenariosHandlers).reduce(
  (acc, scenarioName) => {
    acc[scenarioName as ScenarioName] = scenarioName as ScenarioName;
    return acc;
  },
  {} as Record<ScenarioName, ScenarioName>,
);

export { scenarios, scenariosHandlers };
