/* eslint-disable no-restricted-imports */

import type {
  Path as BasePath,
  LinkProps as BaseLinkProps,
  Location as BaseLocation,
  MemoryRouterProps as BaseMemoryRouterProps,
  PathPattern,
  NavigateOptions as BaseNavigateOptions,
  RedirectFunction as BaseRedirectFunction,
} from "react-router-dom";
import {
  createSearchParams as baseCreateSearchParams,
  Link as BaseLink,
  useNavigate as baseUseNavigate,
  useSearchParams as baseUseSearchParams,
  matchPath as baseMatchPath,
  useLocation as baseUseLocation,
  MemoryRouter as BaseMemoryRouter,
  redirect as baseRedirect,
} from "react-router-dom";

import type { RoutePath } from "@/config/routes";

export type Path = Partial<Exclude<BasePath, "pathname"> & { pathname: RoutePath }>;
export type To = RoutePath | Path;
export type Location = Exclude<BaseLocation, "pathname"> & { pathname: RoutePath };
export type LinkProps = Exclude<BaseLinkProps, "to"> & {
  to: To;
};
export type InitialEntry = RoutePath | Partial<Location>;
export type MemoryRouterProps = BaseMemoryRouterProps & { initialEntries?: InitialEntry[] };

export const Link: (props: LinkProps) => ReturnType<typeof BaseLink> = BaseLink;

type UseLocation = () => Location;
export const useLocation = baseUseLocation as UseLocation;
export const createSearchParams = baseCreateSearchParams;

type NavigateOptions = BaseNavigateOptions;
export interface NavigateFunction {
  (to: To, options?: NavigateOptions): void;
  (delta: number): void;
}
export const useNavigate = baseUseNavigate;
export const MemoryRouter = BaseMemoryRouter;
export const useSearchParams = baseUseSearchParams;
type MatchPath = (
  pattern: PathPattern<string> | RoutePath | `${RoutePath}/*`,
  pathname: string,
) => ReturnType<typeof baseMatchPath>;
export const matchPath = baseMatchPath as MatchPath;
export type RedirectFunction = (url: RoutePath, init?: number | ResponseInit) => ReturnType<BaseRedirectFunction>;
export const redirect = baseRedirect as RedirectFunction;

export {
  createBrowserRouter,
  createRoutesFromElements,
  Route,
  Outlet,
  BrowserRouter,
  createMemoryRouter,
  RouterProvider,
} from "react-router-dom";
