export const protectedRoutes = {
  sites: {
    path: "/sites",
    title: "",
  },
  sitesList: {
    path: "/sites/list",
    title: "Sites List",
  },
  sitesMap: {
    path: "/sites/map",
    title: "Sites Map",
  },
  settings: {
    path: "/settings",
    title: "",
  },
  requests: {
    path: "/settings/requests",
    title: "Requests",
  },
  tokens: {
    path: "/settings/tokens",
    title: "Tokens",
  },
  users: {
    path: "/settings/users",
    title: "Users",
  },
  account: {
    path: "/account",
    title: "",
  },
  personalDetails: {
    path: "/account/details",
    title: "Personal Details",
  },
  password: {
    path: "/account/password",
    title: "Password",
  },
  logout: {
    path: "/logout",
    title: "",
  },
} as const;

export const publicRoutes = {
  index: { path: "/", title: "" },
  login: {
    path: "/login",
    title: "Login",
  },
} as const;

export const routesConfig = { ...publicRoutes, ...protectedRoutes } as const;

// pages without redirect routes
export const protectedPages = Object.values(protectedRoutes).filter((route) => route.title);
export const publicPages = Object.values(publicRoutes).filter((route) => route.title);
export const pages = [...protectedPages, ...publicPages];

type RoutesConfig = typeof routesConfig;
export type RoutePath = RoutesConfig[keyof RoutesConfig]["path"];
