import Chance from "chance";
import { sub, add } from "date-fns";
import { Factory } from "fishery";
import { uniqueNamesGenerator, adjectives, colors, animals, starWars } from "unique-names-generator";

import type { Token } from "@/api/types";
import type {
  PendingSite,
  AccessTokenResponse,
  SitesGetResponse,
  UsersGetResponse,
  PendingSitesGetResponse,
} from "@/api-client";
import { ConnectionStatus } from "@/api-client/models/ConnectionStatus";
import type { Site } from "@/api-client/models/Site";
import type { SiteData } from "@/api-client/models/SiteData";
import { TimeZone } from "@/api-client/models/TimeZone";
import type { User } from "@/api-client/models/User";
import type { SiteMarkerType } from "@/components/Map/types";

export const connections: ConnectionStatus[] = [
  ConnectionStatus.STABLE,
  ConnectionStatus.LOST,
  ConnectionStatus.UNKNOWN,
];

export const statsFactory = Factory.define<SiteData>(({ sequence }) => {
  const chance = new Chance(`maas-${sequence}`);
  const now = new Date();
  const machines = {
    machines_deployed: chance.integer({ min: 0, max: 500 }),
    machines_allocated: chance.integer({ min: 0, max: 500 }),
    machines_ready: chance.integer({ min: 0, max: 500 }),
    machines_error: chance.integer({ min: 0, max: 500 }),
    machines_other: chance.integer({ min: 0, max: 500 }),
  };
  return {
    ...machines,
    machines_total: Object.values(machines).reduce((acc, val) => acc + val, 0),
    last_seen: new Date(chance.date({ min: sub(now, { minutes: 15 }), max: now })).toISOString(),
  };
});

export const connectionFactory = Factory.define<Site["connection_status"]>(({ sequence }) => {
  return uniqueNamesGenerator({
    dictionaries: [connections],
    seed: sequence,
  }) as Site["connection_status"];
});

export const markerFactory = Factory.define<SiteMarkerType>(({ sequence }) => {
  const chance = new Chance(`maas-${sequence}`);
  return {
    id: sequence,
    position: [chance.latitude(), chance.longitude()],
  };
});

const coordinatesFactory = Factory.define<Site["coordinates"]>(({ sequence }) => {
  const chance = new Chance(`maas-${sequence}`);
  return [chance.latitude(), chance.longitude()];
});

export const siteFactory = Factory.define<NonNullable<Site>>(({ sequence }) => {
  const chance = new Chance(`maas-${sequence}`);
  const name = uniqueNamesGenerator({
    dictionaries: [adjectives, colors, animals],
    separator: "-",
    length: 2,
    seed: sequence,
  });

  const site = {
    id: sequence,
    name,
    name_unique: chance.bool(),
    url: `http://${name}.${chance.tld()}`,
    country: chance.country(), // <alpha2 country code>,
    city: chance.city(),
    note: "",
    region: null,
    coordinates: coordinatesFactory.build(),
    postal_code: chance.zip(),
    address: chance.address(),
    state: chance.province(),
    timezone: chance.pickone(Object.values(TimeZone)),
    connection_status: connectionFactory.build(),
    stats: statsFactory.build() as SiteData,
  } as const;
  return site;
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
  const id = sequence;

  return {
    full_name,
    username,
    email,
    is_admin,
    id,
  };
});

export const enrollmentRequestQueryResultFactory = Factory.define<PendingSitesGetResponse>(() => {
  return { items: [], total: 0, page: 0, size: 0 };
});
export const sitesQueryResultFactory = Factory.define<SitesGetResponse>(() => {
  return { items: [], total: 0, page: 0, size: 0 };
});
export const usersQueryResultFactory = Factory.define<UsersGetResponse>(() => {
  return { items: [], total: 0, page: 0, size: 0 };
});

export const durationFactory = Factory.define<string>(() => "P7DT0H0M0S");
export const tokenFactory = Factory.define<Token>(({ sequence }) => {
  const now = new Date();
  const chance = new Chance(`maas-${sequence}`);
  return {
    id: sequence,
    value: chance.hash({ length: 64 }),
    expired: new Date(chance.date({ min: add(now, { seconds: 1 }), max: add(now, { days: 1 }) })).toISOString(), //<ISO 8601 date string>,
    created: new Date(chance.date({ min: sub(now, { minutes: 15 }), max: now })).toISOString(), //<ISO 8601 date string>
  };
});

export const accessTokenFactory = Factory.define<AccessTokenResponse>(({ sequence }) => {
  const chance = new Chance(`maas-${sequence}`);
  return {
    access_token: chance.hash({ length: 64 }),
    token_type: "bearer",
  };
});

export const enrollmentRequestFactory = Factory.define<PendingSite>(({ sequence }) => {
  const chance = new Chance(`maas-${sequence}`);
  const name = uniqueNamesGenerator({
    dictionaries: [adjectives, colors, animals],
    separator: "-",
    length: 2,
    seed: sequence,
  });
  return {
    id: sequence,
    name,
    url: `http://${name}.${chance.tld()}`,
    created: new Date(chance.date({ year: 2023 })).toISOString(), //<ISO 8601 date string>
  };
});

// TODO: replace with auto-generated types from the API client https://warthogs.atlassian.net/browse/MAASENG-2570
export type Image = {
  id: number;
  release: string;
  architecture: string;
  name: string;
  size: number;
  downloaded: number;
  number_of_sites_synced: number;
  is_custom_image: boolean;
  last_synced: Date;
};

export const imageFactory = Factory.define<Image>(() => ({
  id: Math.floor(Math.random() * 1000),
  release: "release",
  architecture: "architecture",
  name: "name",
  size: Math.floor(Math.random() * 10000),
  downloaded: Math.floor(Math.random() * 100),
  number_of_sites_synced: Math.floor(Math.random() * 100),
  is_custom_image: Math.random() < 0.5,
  last_synced: new Date(),
}));
