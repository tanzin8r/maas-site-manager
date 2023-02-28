export type Site = {
  name: string;
  url: string; // <full URL including protocol>,
  connection: "stable" | "stale" | "lost";
  last_seen: string; // <ISO 8601 date>,
  address: {
    countrycode: string; // <alpha2 country code>,
    city: string;
    zip: string;
    street: string;
  };
  timezone: string; // <three letter abbreviation>,
  stats: {
    machines: number;
    occupied_machines: number;
    ready_machines: number;
    error_machines: number;
  };
};

export type Sites = {
  items: Site[];
  total: number;
  page: number;
  size: number;
};
