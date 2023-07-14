import Chance from "chance";
import { sub, add } from "date-fns";
import { Factory } from "fishery";
import { uniqueNamesGenerator, adjectives, colors, animals, starWars } from "unique-names-generator";

import type { AccessToken, EnrollmentRequest, PaginatedQueryResult, Site, Stats, Token, User } from "@/api/types";

export const connections: Stats["connection"][] = ["stable", "lost", "unknown"];

export const statsFactory = Factory.define<Stats>(({ sequence }) => {
  const chance = new Chance(`maas-${sequence}`);
  const now = new Date();
  const machines = {
    deployed_machines: chance.integer({ min: 0, max: 500 }),
    allocated_machines: chance.integer({ min: 0, max: 500 }),
    ready_machines: chance.integer({ min: 0, max: 500 }),
    error_machines: chance.integer({ min: 0, max: 500 }),
  };
  return {
    ...machines,
    total_machines: Object.values(machines).reduce((acc, val) => acc + val, 0),
    last_seen: new Date(chance.date({ min: sub(now, { minutes: 15 }), max: now })).toISOString(),
    connection: connectionFactory.build(),
  };
});

export const connectionFactory = Factory.define<Stats["connection"]>(({ sequence }) => {
  return uniqueNamesGenerator({
    dictionaries: [connections],
    seed: sequence,
  }) as Stats["connection"];
});

export const siteFactory = Factory.define<Site>(({ sequence }) => {
  const chance = new Chance(`maas-${sequence}`);
  const name = uniqueNamesGenerator({
    dictionaries: [adjectives, colors, animals],
    separator: "-",
    length: 2,
    seed: sequence,
  });

  return {
    id: `${sequence}`,
    name,
    name_unique: chance.bool(),
    url: `http://${name}.${chance.tld()}`,
    country: chance.country(), // <alpha2 country code>,
    city: chance.city(),
    zip: chance.zip(),
    street: chance.address(),
    timezone: chance.timezone().utc[0],
    stats: statsFactory.build(),
  };
});

export const userFactory = Factory.define<User>(({ sequence }) => {
  const chance = new Chance(`maas-${sequence}`);

  const full_name = uniqueNamesGenerator({
    dictionaries: [starWars],
    length: 1,
    seed: sequence,
  });
  // .replace("é", "e") <-- This is to make sure usernames and email addresses are valid.
  const username = `${full_name.replace(/\s/g, "").replace("é", "e")}${chance.integer({ min: 1, max: 99 })}`;
  const email = `${username}@galactic-republic.gov`.toLowerCase().replace("é", "e");
  const is_admin = chance.bool();

  return {
    id: sequence,
    full_name,
    username,
    email,
    is_admin,
  };
});

export const paginatedQueryResultFactory = <T extends unknown>() =>
  Factory.define<PaginatedQueryResult<T>>(() => {
    return { items: [], total: 0, page: 0, size: 0 };
  });

export const enrollmentRequestQueryResultFactory = paginatedQueryResultFactory<EnrollmentRequest>();
export const sitesQueryResultFactory = paginatedQueryResultFactory<Site>();
export const usersQueryResultFactory = paginatedQueryResultFactory<User>();

export const durationFactory = Factory.define<string>(() => "P7DT0H0M0S");
export const tokenFactory = Factory.define<Token>(({ sequence }) => {
  const now = new Date();
  const chance = new Chance(`maas-${sequence}`);
  return {
    id: sequence,
    site_id: `${chance.integer({ min: 0, max: 100 })}`,
    value: chance.hash({ length: 64 }),
    expired: new Date(chance.date({ min: add(now, { seconds: 1 }), max: add(now, { days: 1 }) })).toISOString(), //<ISO 8601 date string>,
    created: new Date(chance.date({ min: sub(now, { minutes: 15 }), max: now })).toISOString(), //<ISO 8601 date string>
  };
});

export const accessTokenFactory = Factory.define<AccessToken>(({ sequence }) => {
  const chance = new Chance(`maas-${sequence}`);
  return {
    access_token: chance.hash({ length: 64 }),
    token_type: "bearer",
  };
});

export const enrollmentRequestFactory = Factory.define<EnrollmentRequest>(({ sequence }) => {
  const chance = new Chance(`maas-${sequence}`);
  const name = uniqueNamesGenerator({
    dictionaries: [adjectives, colors, animals],
    separator: "-",
    length: 2,
    seed: sequence,
  });
  return {
    id: `request-${sequence}`,
    name,
    url: `http://${name}.${chance.tld()}`,
    created: new Date(chance.date({ year: 2023 })).toISOString(), //<ISO 8601 date string>
  };
});
