import type { RoutePath, RouteTitle } from "@/config/routes";

type BaseNavLink = {
  adminOnly?: boolean;
  external?: boolean;
  icon?: string;
  label: RouteTitle;
};
export type ExternalNavLink = {
  external: true;
  url: string;
  icon?: string;
  label: string;
  highlight?: never;
};

export type LocalNavLink = BaseNavLink & {
  external?: false;
  url: RoutePath;
  highlight?: RoutePath | RoutePath[];
};
export type NavLink = ExternalNavLink | LocalNavLink;

export type NavGroup = {
  navLinks: NavLink[];
  groupTitle?: string;
  groupIcon?: string;
};

export type NavItem = NavGroup | NavLink;
