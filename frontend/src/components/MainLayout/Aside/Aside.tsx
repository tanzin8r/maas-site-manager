import { Suspense, useEffect } from "react";

import { Col, Row, useOnEscapePressed, usePrevious } from "@canonical/react-components";
import classNames from "classnames";

import { useAppLayoutContext } from "@/context";
import type { Sidebar } from "@/context/AppLayoutContext";
import { useLocation } from "@/utils/router";

export const sidebarLabels: Record<NonNullable<Sidebar>, string> = {
  addUser: "Add user",
  editUser: "Edit user",
  removeSites: "Remove sites",
  createToken: "Generate tokens",
  deleteUser: "Delete user",
  siteDetails: "Site details",
  editSite: "Edit site",
  siteSelect: "Selected Sites",
  uploadImage: "Upload image",
  downloadImages: "Download images",
  deleteImages: "Delete images",
  deleteOrKeepImages: "Delete images",
};

export const sidebarComponent: Record<NonNullable<Sidebar>, React.FC> = {
  addUser: lazy(() => import("@/components/UserForm/UserAddForm")),
  editSite: lazy(() => import("@/components/EditSite")),
  editUser: lazy(() => import("@/components/UserForm/UserEditForm")),
  createToken: lazy(() => import("@/components/TokensCreate")),
  deleteUser: lazy(() => import("@/components/DeleteUser")),
  removeSites: lazy(() => import("@/components/RemoveSites")),
  siteDetails: lazy(() => import("@/components/SiteDetails")),
  siteSelect: () => null,
  uploadImage: lazy(() => import("@/components/UploadImage")),
  downloadImages: lazy(() => import("@/components/DownloadImages")),
  deleteImages: lazy(() => import("@/components/DeleteImages")),
  deleteOrKeepImages: lazy(() => import("@/components/DeleteOrKeepImages")),
} as const;

export const SidebarComponents = ({ sidebar }: { sidebar: NonNullable<Sidebar> }) => {
  const ComponentToRender = sidebarComponent[sidebar] || null;

  return <ComponentToRender />;
};

export const Aside = () => {
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
      className={classNames("l-aside is-maas-site-manager", { "is-collapsed": !sidebar })}
      id="aside-panel"
    >
      <Row>
        <Col size={12}>
          <Suspense>{sidebar && <SidebarComponents sidebar={sidebar} />}</Suspense>
        </Col>
      </Row>
    </aside>
  );
};
