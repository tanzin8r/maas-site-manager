import type { RoutePath } from "@/config/routes";

type BaseNavLink = {
  adminOnly?: boolean;
  external?: boolean;
  icon?: string | React.ReactNode;
  label: string;
};
export type ExternalNavLink = BaseNavLink & {
  external: true;
  url: string;
  highlight?: RoutePath | RoutePath[];
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
  groupIcon?: string | React.ReactNode;
};

export type NavItem = NavGroup | NavLink;
