import type { PropsWithChildren } from "react";
import { useEffect } from "react";

import { Col, Row, Strip, useOnEscapePressed, usePrevious } from "@canonical/react-components";
import classNames from "classnames";
import { matchPath, Outlet, useLocation } from "react-router-dom";

import { routesConfig } from "@/base/routesConfig";
import type { RoutePath } from "@/base/routesConfig";
import DocumentTitle from "@/components/DocumentTitle/DocumentTitle";
import Navigation from "@/components/Navigation";
import NavigationBanner from "@/components/Navigation/NavigationBanner";
import RemoveRegions from "@/components/RemoveRegions";
import SecondaryNavigation from "@/components/SecondaryNavigation";
import { useAppContext } from "@/context";
import TokensCreate from "@/pages/tokens/create";

export const sidebarLabels: Record<"removeRegions" | "createToken", string> = {
  removeRegions: "Remove regions",
  createToken: "Generate tokens",
};

type AsideProps = PropsWithChildren<Pick<ReturnType<typeof useAppContext>, "sidebar" | "setSidebar">>;
const Aside = ({ children, sidebar, setSidebar, ...props }: AsideProps) => {
  useOnEscapePressed(() => {
    setSidebar(null);
  });
  return (
    <aside
      aria-hidden={!sidebar}
      className={classNames("l-aside is-maas-site-manager u-padding-top--medium", { "is-collapsed": !sidebar })}
      id="aside-panel"
      role="dialog"
      {...props}
    >
      <Row>
        <Col size={12}>{children}</Col>
      </Row>
    </aside>
  );
};

const getPageTitle = (pathname: RoutePath) => {
  const title = Object.values(routesConfig).find(({ path }) => path === pathname)?.title;
  return title ? `${title} | MAAS Site Manager` : "MAAS Site Manager";
};

const LoginLayout: React.FC = () => {
  const { pathname } = useLocation();
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
        <h1 className="u-hide">{getPageTitle(pathname as RoutePath)}</h1>
        <div className="l-main__content">
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

  const isSideNavVisible = matchPath("settings/*", pathname);

  return (
    <>
      <div className="l-application">
        <Navigation />
        <main className="l-main is-maas-site-manager">
          <h1 className="u-hide">{getPageTitle(pathname as RoutePath)}</h1>
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
        <Aside aria-label={sidebar ? sidebarLabels[sidebar] : undefined} setSidebar={setSidebar} sidebar={sidebar}>
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
