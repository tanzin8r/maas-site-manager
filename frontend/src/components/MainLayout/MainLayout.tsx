import { Suspense } from "react";

import classNames from "classnames";

import { Aside } from "./Aside";

import DocumentTitle from "@/components/DocumentTitle/DocumentTitle";
import Navigation from "@/components/Navigation";
import SecondaryNavigation from "@/components/SecondaryNavigation";
import type { RoutePath } from "@/config/routes";
import { routesConfig } from "@/config/routes";
import { useAuthContext } from "@/context";
import { matchPath, Outlet, useLocation } from "@/utils/router";

const getPageTitle = (pathname: RoutePath) => {
  const title = Object.values(routesConfig).find(({ path }) => path === pathname)?.title;
  return title ? `${title} | MAAS Site Manager` : "MAAS Site Manager";
};

const MainLayout: React.FC = () => {
  const { pathname } = useLocation();
  const { status } = useAuthContext();
  const isLoggedIn = status === "authenticated";
  const isSideNavVisible = matchPath("/settings/*", pathname) || matchPath("/account/*", pathname);

  return (
    <div className="l-application">
      <Navigation isLoggedIn={isLoggedIn} />
      <main className="l-main is-maas-site-manager">
        <h1 className="u-visually-hidden">{getPageTitle(pathname as RoutePath)}</h1>
        <div className={classNames("l-main__nav", { "is-open": isSideNavVisible })}>
          <SecondaryNavigation isOpen={!!isSideNavVisible} />
        </div>
        <div className="l-main__content">
          <div className="row">
            <div className="col-12">
              <Suspense>
                <Outlet />
              </Suspense>
            </div>
          </div>
        </div>
      </main>
      <Aside />
    </div>
  );
};

const Layout = () => {
  const { pathname } = useLocation();
  return (
    <>
      <DocumentTitle>{getPageTitle(pathname as RoutePath)}</DocumentTitle>
      <MainLayout />
    </>
  );
};

export default Layout;
