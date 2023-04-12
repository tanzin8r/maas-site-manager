export type AccessToken = {
  access_token: string;
  token_type: "bearer";
};

export type Site = {
  identifier: string;
  name: string;
  url: string; // <full URL including protocol>,
  connection: "stable" | "lost" | "unknown";
  last_seen: string; // <ISO 8601 date>,
  address: {
    countrycode: string; // <alpha2 country code>,
    city: string;
    zip: string;
    street: string;
  };
  timezone: number;
  stats: {
    machines: number;
    occupied_machines: number;
    ready_machines: number;
    error_machines: number;
  };
};

export type PaginatedQueryResult<D extends unknown> = {
  items: D[];
  total: number;
  page: number;
  size: number;
};

export type SitesQueryResult = PaginatedQueryResult<Site>;

export type Token = {
  name: string;
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
