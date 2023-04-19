export const protectedRoutes = {
  sites: {
    path: "/sites",
    title: "Regions",
  },
  requests: {
    path: "/settings/requests",
    title: "Requests",
  },
  tokens: {
    path: "/settings/tokens",
    title: "Tokens",
  },
};
export const publicRoutes = {
  login: {
    path: "/login",
    title: "Login",
  },
};

export const routesConfig = { ...publicRoutes, ...protectedRoutes } as const;

type RoutesConfig = typeof routesConfig;
export type RoutePath = RoutesConfig[keyof RoutesConfig]["path"];
