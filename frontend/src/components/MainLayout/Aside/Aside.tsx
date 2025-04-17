import { Suspense, useEffect } from "react";

import { ContentSection } from "@canonical/maas-react-components";
import { Col, Row, Spinner, useOnEscapePressed, usePrevious, AppAside } from "@canonical/react-components";

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
  sitesMissingData: "Sites with missing data",
  deleteBootSource: "Delete image source",
  addBootSource: "Add image source",
  editBootSource: "Edit image source",
  editCustomImagesSource: "Edit custom images",
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
  sitesMissingData: lazy(() => import("@/components/SitesMissingData")),
  deleteBootSource: lazy(() => import("@/components/DeleteImageSource")),
  addBootSource: lazy(() => import("@/components/ImageSourceForm/AddImageSourceForm")),
  editBootSource: lazy(() => import("@/components/ImageSourceForm/EditImageSourceForm")),
  editCustomImagesSource: lazy(() => import("@/components/ImageSourceForm/EditCustomImagesSourceForm")),
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
    <AppAside
      aria-hidden={!sidebar}
      aria-label={sidebar ? sidebarLabels[sidebar] : undefined}
      className="is-maas-site-manager"
      collapsed={!sidebar}
      id="aside-panel"
    >
      <Row>
        <Col size={12}>
          <Suspense
            fallback={
              <ContentSection>
                <Spinner text="Loading..." />
              </ContentSection>
            }
          >
            {sidebar && <SidebarComponents sidebar={sidebar} />}
          </Suspense>
        </Col>
      </Row>
    </AppAside>
  );
};
