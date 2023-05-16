import { useEffect } from "react";

import { Col, Row, useOnEscapePressed, usePrevious } from "@canonical/react-components";
import classNames from "classnames";

import { routesConfig } from "@/base/routesConfig";
import type { RoutePath } from "@/base/routesConfig";
import DocumentTitle from "@/components/DocumentTitle/DocumentTitle";
import Navigation from "@/components/Navigation";
import RemoveRegions from "@/components/RemoveRegions";
import SecondaryNavigation from "@/components/SecondaryNavigation";
import { useAppContext, useAuthContext } from "@/context";
import TokensCreate from "@/pages/tokens/create";
import { matchPath, Outlet, useLocation } from "@/router";

export const sidebarLabels: Record<"removeRegions" | "createToken", string> = {
  removeRegions: "Remove regions",
  createToken: "Generate tokens",
};

const Aside = () => {
  const { pathname } = useLocation();
  const previousPathname = usePrevious(pathname);
  const { sidebar, setSidebar } = useAppContext();

  // close any open panels on route change
  useEffect(() => {
    if (pathname !== previousPathname) {
      setSidebar(null);
    }
  }, [pathname, previousPathname, setSidebar]);

  useOnEscapePressed(() => {
    setSidebar(null);
  });

  return (
    <aside
      aria-hidden={!sidebar}
      aria-label={sidebar ? sidebarLabels[sidebar] : undefined}
      className={classNames("l-aside is-maas-site-manager u-padding-top--medium", { "is-collapsed": !sidebar })}
      id="aside-panel"
      role="dialog"
    >
      <Row>
        <Col size={12}>
          {sidebar === "createToken" ? <TokensCreate /> : sidebar === "removeRegions" ? <RemoveRegions /> : null}
        </Col>
      </Row>
    </aside>
  );
};

const getPageTitle = (pathname: RoutePath) => {
  const title = Object.values(routesConfig).find(({ path }) => path === pathname)?.title;
  return title ? `${title} | MAAS Site Manager` : "MAAS Site Manager";
};

const MainLayout: React.FC = () => {
  const { pathname } = useLocation();
  const { status } = useAuthContext();
  const isLoggedIn = status === "authenticated";
  const isSideNavVisible = matchPath("/settings/*", pathname);

  return (
    <div className="l-application">
      <Navigation isLoggedIn={isLoggedIn} />
      <main className="l-main is-maas-site-manager">
        <h1 className="u-visually-hidden">{getPageTitle(pathname as RoutePath)}</h1>
        <div className={classNames("l-main__nav", { "is-open": isSideNavVisible })}>
          <SecondaryNavigation isOpen={!!isSideNavVisible} />
        </div>
        <div className="l-main__content u-padding-top--medium">
          <div className="row">
            <div className="col-12">
              <Outlet />
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
