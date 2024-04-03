import { setupWorker } from "msw";

import { allResolvers } from "./resolvers";
import type { ScenarioName } from "./scenarios";
import { scenariosHandlers } from "./scenarios";
const scenarioName = new URLSearchParams(window.location.search).get("scenario");
const runtimeScenarios = scenarioName ? scenariosHandlers[scenarioName as ScenarioName] : [];

export const worker = setupWorker(...runtimeScenarios, ...allResolvers);
