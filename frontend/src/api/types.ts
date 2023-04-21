export type AccessToken = {
  access_token: string;
  token_type: "bearer";
};

export type Stats = {
  allocated_machines: number;
  deployed_machines: number;
  ready_machines: number;
  error_machines: number;
  last_seen: string; // <ISO 8601 date string>
  connection: "stable" | "lost" | "unknown";
};

export type Site = {
  id: string;
  name: string;
  url: string; // <full URL including protocol>,
  connection: Stats["connection"];
  last_seen: string; // <ISO 8601 date>,
  address: {
    countrycode: string; // <alpha2 country code>,
    city: string;
    zip: string;
    street: string;
  };
  timezone: string; // IANA time zone name,
  stats: Stats;
};

export type PaginatedQueryResult<D extends unknown> = {
  items: D[];
  total: number;
  page: number;
  size: number;
};

export type SitesQueryResult = PaginatedQueryResult<Site>;

export type Token = {
  id: string;
  site_id: Site["id"] | null;
  token: string;
  expires: string; //<ISO 8601 date string>,
  created: string; //<ISO 8601 date string>
};
export type PostTokensResult = PaginatedQueryResult<Token>;

export type EnrollmentRequest = {
  id: string;
  name: string;
  url: string;
  created: string; // <ISO 8601 date>,
};

export type EnrollmentRequestsQueryResult = PaginatedQueryResult<EnrollmentRequest>;
