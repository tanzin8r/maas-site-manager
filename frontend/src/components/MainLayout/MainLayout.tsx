import type { PropsWithChildren } from "react";
import { useEffect } from "react";

import { Col, Row, Strip, usePrevious } from "@canonical/react-components";
import classNames from "classnames";
import { Outlet, useLocation } from "react-router-dom";

import { routesConfig } from "@/base/routesConfig";
import type { RoutePath } from "@/base/routesConfig";
import DocumentTitle from "@/components/DocumentTitle/DocumentTitle";
import Navigation from "@/components/Navigation";
import NavigationBanner from "@/components/Navigation/NavigationBanner";
import RemoveRegions from "@/components/RemoveRegions";
import { useAppContext } from "@/context";
import TokensCreate from "@/pages/tokens/create";

export const sidebarLabels: Record<"removeRegions" | "createToken", string> = {
  removeRegions: "Remove regions",
  createToken: "Generate tokens",
};

const Aside = ({ children, isOpen, ...props }: PropsWithChildren<{ isOpen: boolean }>) => (
  <aside
    aria-hidden={!isOpen}
    className={classNames("l-aside", "is-maas-site-manager", { "is-collapsed": !isOpen })}
    id="aside-panel"
    role="dialog"
    {...props}
  >
    <Row>
      <Col size={12}>{children}</Col>
    </Row>
  </aside>
);

const getPageTitle = (pathname: RoutePath) => {
  const title = Object.values(routesConfig).find(({ path }) => path === pathname)?.title;
  return title ? `${title} | MAAS Site Manager` : "MAAS Site Manager";
};

const LoginLayout: React.FC = () => {
  return (
    <div className="l-application">
      <header className="l-navigation-bar is-pinned">
        <div className="p-panel is-dark">
          <div className="p-panel__header">
            <NavigationBanner />
          </div>
        </div>
      </header>
      <main className="l-main">
        <div>
          <Strip element="section" includeCol={false} shallow>
            <Col size={12}>
              <Outlet />
            </Col>
          </Strip>
        </div>
      </main>
    </div>
  );
};

const MainLayout: React.FC = () => {
  const { sidebar, setSidebar } = useAppContext();
  const { pathname } = useLocation();
  const previousPathname = usePrevious(pathname);

  // close any open panels on route change
  useEffect(() => {
    if (pathname !== previousPathname) {
      setSidebar(null);
    }
  }, [pathname, previousPathname, setSidebar]);

  return (
    <>
      <div className="l-application">
        <Navigation />
        <main className="l-main is-maas-site-manager">
          <div className="row">
            <div className="col-12">
              <h1 className="u-hide">MAAS Site Manager</h1>
              <Outlet />
            </div>
          </div>
        </main>
        <Aside aria-label={sidebar ? sidebarLabels[sidebar] : undefined} isOpen={!!sidebar}>
          {!!sidebar && sidebar === "createToken" ? (
            <TokensCreate />
          ) : !!sidebar && sidebar === "removeRegions" ? (
            <RemoveRegions />
          ) : null}
        </Aside>
      </div>
    </>
  );
};

const Layout = () => {
  const { pathname } = useLocation();
  return (
    <>
      <DocumentTitle>{getPageTitle(pathname as RoutePath)}</DocumentTitle>
      {pathname === "/login" ? <LoginLayout /> : <MainLayout />}
    </>
  );
};

export default Layout;
