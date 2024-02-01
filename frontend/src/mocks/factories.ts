import Chance from "chance";
import { sub, add } from "date-fns";
import { Factory } from "fishery";
import { uniqueNamesGenerator, adjectives, colors, animals, starWars } from "unique-names-generator";

import type { UpstreamImageSource, TSettings } from "@/api/handlers";
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
  last_synced: string | null; // <ISO 8601 date string>
};

// TODO: replace with auto-generated types from the API client https://warthogs.atlassian.net/browse/MAASENG-2569
export type UpstreamImage = Pick<Image, "id" | "release" | "architecture" | "name" | "size">;

// TODO: replace with actual Settings type
// once settings api is updated
// https://warthogs.atlassian.net/browse/MAASENG-2594
export const settingsFactory = Factory.define<TSettings>(() => ({
  service_url: "http://localhost:3000",
  images_connect_to_maas: true,
}));

const ubuntuReleaseFactory = Factory.define<string>(({ sequence }) => {
  const chance = new Chance(`maas-${sequence}`);
  return chance.pickone(["23.10", "23.04", "22.10", "22.04 LTS"]);
});

const archFactory = Factory.define<string>(({ sequence }) => {
  const chance = new Chance(`maas-${sequence}`);
  return chance.pickone(["amd64", "arm64", "i386", "armhf"]);
});
const osFactory = Factory.define<{ name: string; release: string }>(({ sequence }) => {
  const chance = new Chance(`${sequence}`);
  return chance.pickone([
    { name: "Ubuntu", release: ubuntuReleaseFactory.build() },
    { name: "CentOS", release: chance.pickone(["8", "7"]) },
    { name: "Windows", release: chance.pickone(["10", "8.1", "7"]) },
    { name: "RHEL", release: chance.pickone(["8", "7"]) },
    { name: "Hannah Montana Linux", release: chance.pickone(["6.0.0-GitGuitar", "7.0.0-CommandLineQueen"]) },
  ]);
});

export const imageFactory = Factory.define<Image>(({ sequence }) => {
  const chance = new Chance(`maas-${sequence}`);
  const OS = osFactory.build();
  return {
    id: sequence,
    release: OS.release,
    architecture: archFactory.build(),
    name: OS.name,
    size: chance.integer({ min: 300 * 1024, max: 4 * 1024 * 1024 }) * 1024,
    downloaded: Math.floor(Math.random() * 3),
    number_of_sites_synced: Math.floor(Math.random() * 2),
    is_custom_image: chance.bool(),
    last_synced: chance.pickone([new Date().toISOString(), null]),
  };
});

export const upstreamImageFactory = Factory.define<UpstreamImage>(({ sequence }) => {
  const chance = new Chance(`maas-${sequence}`);
  const OS = osFactory.build();
  return {
    id: sequence,
    release: OS.release,
    architecture: archFactory.build(),
    name: OS.name,
    size: Math.floor(chance.floating({ min: 0, max: 1 }) * 10000),
  };
});

export const upstreamImageSourceFactory = Factory.define<Omit<UpstreamImageSource, "credentials">>(({ sequence }) => {
  const chance = new Chance(`maas-${sequence}`);

  return {
    keepUpdated: chance.bool(),
    upstreamSource: `https://images.${chance.domain()}.com`,
  };
});
