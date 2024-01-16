import { useEffect } from "react";

import { Col, Row, useOnEscapePressed, usePrevious } from "@canonical/react-components";
import classNames from "classnames";

import DeleteImages from "@/components/DeleteImages";
import DeleteUser from "@/components/DeleteUser";
import DownloadImages from "@/components/DownloadImages";
import EditSite from "@/components/EditSite";
import RemoveSites from "@/components/RemoveSites";
import SiteDetails from "@/components/SiteDetails";
import SiteSelection from "@/components/SiteSelection/SiteSelection";
import { UploadImage } from "@/components/UploadImage";
import UserForm from "@/components/UserForm";
import { useAppLayoutContext } from "@/context";
import type { Sidebar } from "@/context/AppLayoutContext";
import { siteFactory } from "@/mocks/factories";
import TokensCreate from "@/routes/tokens/create";
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
};

const mockSelectedSites = siteFactory.buildList(3);

const UserAddForm = () => <UserForm type="add" />;
const UserEditForm = () => <UserForm type="edit" />;
const SiteSelectionComponent = () => <SiteSelection selectedSites={mockSelectedSites} />;

export const sidebarComponent: Record<NonNullable<Sidebar>, React.FC> = {
  addUser: UserAddForm,
  editSite: EditSite,
  editUser: UserEditForm,
  createToken: TokensCreate,
  deleteUser: DeleteUser,
  removeSites: RemoveSites,
  siteDetails: SiteDetails,
  siteSelect: SiteSelectionComponent,
  uploadImage: UploadImage,
  downloadImages: DownloadImages,
  deleteImages: DeleteImages,
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
        <Col size={12}>{sidebar && <SidebarComponents sidebar={sidebar} />}</Col>
      </Row>
    </aside>
  );
};
