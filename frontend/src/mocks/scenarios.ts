import { rest } from "msw";

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
    rest.get(getApiUrl("/sites"), (req, res, ctx) => {
      return res(ctx.status(401), ctx.json({ error: "Unauthorized" }));
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
