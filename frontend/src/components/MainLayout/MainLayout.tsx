import { useEffect } from "react";

import { Col, Row, useOnEscapePressed, usePrevious } from "@canonical/react-components";
import classNames from "classnames";

import DeleteUser from "@/components/DeleteUser";
import DocumentTitle from "@/components/DocumentTitle/DocumentTitle";
import EditSite from "@/components/EditSite";
import Navigation from "@/components/Navigation";
import RemoveSites from "@/components/RemoveSites";
import SecondaryNavigation from "@/components/SecondaryNavigation";
import SiteDetails from "@/components/SiteDetails";
import SiteSelection from "@/components/SiteSelection/SiteSelection";
import UserForm from "@/components/UserForm";
import type { RoutePath } from "@/config/routes";
import { routesConfig } from "@/config/routes";
import { useAppLayoutContext, useAuthContext } from "@/context";
import type { Sidebar } from "@/context/AppLayoutContext";
import { siteFactory } from "@/mocks/factories";
import TokensCreate from "@/pages/tokens/create";
import { matchPath, Outlet, useLocation } from "@/utils/router";

export const sidebarLabels: Record<NonNullable<Sidebar>, string> = {
  addUser: "Add user",
  editUser: "Edit user",
  removeSites: "Remove sites",
  createToken: "Generate tokens",
  deleteUser: "Delete user",
  siteDetails: "Site details",
  editSite: "Edit site",
  siteSelect: "Selected Sites",
};

const mockSelectedSites = siteFactory.buildList(3);

const UserAddForm = () => <UserForm type="add" />;
const UserEditForm = () => <UserForm type="edit" />;
const SiteSelectionComponent = () => <SiteSelection selectedSites={mockSelectedSites} />;

const sidebarComponent = {
  addUser: UserAddForm,
  editSite: EditSite,
  editUser: UserEditForm,
  createToken: TokensCreate,
  deleteUser: DeleteUser,
  removeSites: RemoveSites,
  siteDetails: SiteDetails,
  siteSelect: SiteSelectionComponent,
} as const;

const SidebarComponents = ({ sidebar }: { sidebar: NonNullable<Sidebar> }) => {
  const ComponentToRender = sidebarComponent[sidebar] || null;

  return <ComponentToRender />;
};

const Aside = () => {
  const { pathname } = useLocation();
  const previousPathname = usePrevious(pathname);
  const { sidebar, setSidebar } = useAppLayoutContext();

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
    >
      <Row>
        <Col size={12}>{sidebar && <SidebarComponents sidebar={sidebar} />}</Col>
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
  const isSideNavVisible = matchPath("/settings/*", pathname) || matchPath("/account/*", pathname);

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
