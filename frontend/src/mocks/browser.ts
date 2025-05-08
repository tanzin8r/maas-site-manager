import { setupWorker } from "msw/browser";

import type { ScenarioName } from "./scenarios";
import { scenariosHandlers } from "./scenarios";

import { allResolvers } from "@/testing/resolvers";
const scenarioName = new URLSearchParams(window.location.search).get("scenario");
const runtimeScenarios = scenarioName ? scenariosHandlers[scenarioName as ScenarioName] : [];

export const worker = setupWorker(...runtimeScenarios, ...allResolvers);
