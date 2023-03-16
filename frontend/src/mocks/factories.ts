import Chance from "chance";
import { Factory } from "fishery";
import { uniqueNamesGenerator, adjectives, colors, animals } from "unique-names-generator";

import type { Site, Token } from "@/api/types";

const connections: Site["connection"][] = ["stable", "lost", "stale", "unstable"];

export const siteFactory = Factory.define<Site>(({ sequence }) => {
  const chance = new Chance(`maas-${sequence}`);
  const name = uniqueNamesGenerator({
    dictionaries: [adjectives, colors, animals],
    separator: "-",
    length: 2,
    seed: sequence,
  });
  const connection = uniqueNamesGenerator({
    dictionaries: [connections],
    seed: sequence,
  }) as Site["connection"];
  return {
    identifier: `${sequence}`,
    name,
    url: `http://${name}.${chance.tld()}`,
    connection,
    last_seen: new Date(chance.date({ year: 2023 })).toISOString(),
    address: {
      countrycode: chance.country(), // <alpha2 country code>,
      city: chance.city(),
      zip: chance.zip(),
      street: chance.address(),
    },
    timezone: "CET", // <three letter abbreviation>,
    stats: {
      machines: chance.integer({ min: 0, max: 1500 }),
      occupied_machines: chance.integer({ min: 0, max: 500 }),
      ready_machines: chance.integer({ min: 0, max: 500 }),
      error_machines: chance.integer({ min: 0, max: 500 }),
    },
  };
});

export const tokenFactory = Factory.define<Token>(({ sequence }) => {
  const chance = new Chance(`maas-${sequence}`);
  return {
    name: `${sequence}`,
    token: chance.hash({ length: 32 }),
    expires: new Date(chance.date({ year: 2024 })).toISOString(), //<ISO 8601 date string>,
    created: new Date(chance.date({ year: 2023 })).toISOString(), //<ISO 8601 date string>
  };
});
