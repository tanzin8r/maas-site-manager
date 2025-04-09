import { Navigation, NavigationBar } from "@canonical/maas-react-components";
import useLocalStorageState from "use-local-storage-state";

import NavigationBanner from "./NavigationBanner";
import NavigationList from "./NavigationList";
import type { ExternalNavLink, LocalNavLink } from "./types";

import BREAKPOINTS from "@/config/breakpoints";
import type { RoutePath } from "@/config/routes";
import { hasImagesPage } from "@/featureFlags";
import { useCurrentUserQuery } from "@/hooks/react-query";
import { useGlobalKeyShortcut } from "@/hooks/useGlobalKeyShortcut";
import { useLocation } from "@/utils/router";

export const navItems: LocalNavLink[] = [
  {
    label: "Sites",
    url: "/sites",
    icon: "machines",
  },
  ...(hasImagesPage
    ? [
        {
          label: "Images",
          url: "/images",
          icon: "applications",
        },
      ]
    : []),
];

export const settingsNavItems: LocalNavLink[] = [
  {
    label: "Settings",
    url: "/settings",
    icon: "settings",
  },
];

const generateNavItemsAccount = (userName = "User"): LocalNavLink[] => [
  { label: userName, url: "/account", icon: "user" },
  { label: "Log out", url: "/logout" },
];

export const navItemsBottom: ExternalNavLink[] = [
  { external: true, icon: "information", label: "Documentation", url: "https://maas.io/docs" },
  { external: true, icon: "comments", label: "Community", url: "https://discourse.maas.io/" },
  {
    external: true,
    icon: "submit-bug",
    label: "Report a bug",
    url: "https://bugs.launchpad.net/maas-site-manager/+filebug",
  },
];

type NavProps = {
  isLoggedIn: boolean;
};

const AccountNavigationList = ({ handleNavlinkClick, path }: { handleNavlinkClick: () => void; path: RoutePath }) => {
  const { data } = useCurrentUserQuery();
  return (
    <NavigationList
      hasIcons
      isDark
      items={generateNavItemsAccount(data?.username)}
      onClick={handleNavlinkClick}
      path={path}
    />
  );
};

const AppNavigation = ({ isLoggedIn }: NavProps): JSX.Element => {
  const [isCollapsed, setIsCollapsed] = useLocalStorageState<boolean>("appSideNavIsCollapsed", { defaultValue: true });
  const location = useLocation();
  const path = location.pathname;

  useEffect(() => {
    if (!isLoggedIn) {
      setIsCollapsed(true);
    }
  }, [isLoggedIn, setIsCollapsed]);

  const handleNavlinkClick = () => {
    if (window.screen.width <= BREAKPOINTS.small) {
      setIsCollapsed(true);
    }
  };

  useGlobalKeyShortcut("[", () => {
    setIsCollapsed(!isCollapsed);
  });

  return (
    <>
      <NavigationBar className="l-navigation-bar">
        <Navigation.Header>
          <NavigationBanner />
          <Navigation.Controls>
            <NavigationBar.MenuButton
              onClick={() => {
                setIsCollapsed(!isCollapsed);
              }}
            >
              Menu
            </NavigationBar.MenuButton>
          </Navigation.Controls>
        </Navigation.Header>
      </NavigationBar>
      <Navigation isCollapsed={isCollapsed}>
        <Navigation.Drawer>
          <Navigation.Header>
            <NavigationBanner>
              <Navigation.Controls>
                <Navigation.CollapseToggle isCollapsed={isCollapsed} setIsCollapsed={setIsCollapsed} />
                <NavigationBar.MenuButton
                  onClick={() => {
                    setIsCollapsed(!isCollapsed);
                  }}
                >
                  Close menu
                </NavigationBar.MenuButton>
              </Navigation.Controls>
            </NavigationBanner>
          </Navigation.Header>
          <Navigation.Content>
            {isLoggedIn && (
              <>
                <NavigationList items={navItems} onClick={handleNavlinkClick} path={path} />
                <NavigationList items={settingsNavItems} onClick={handleNavlinkClick} path={path} />
                <AccountNavigationList handleNavlinkClick={handleNavlinkClick} path={path} />
              </>
            )}
          </Navigation.Content>
          <Navigation.Footer>
            <Navigation.Content>
              <NavigationList hideDivider items={navItemsBottom} onClick={handleNavlinkClick} path={path} />
            </Navigation.Content>
          </Navigation.Footer>
        </Navigation.Drawer>
      </Navigation>
    </>
  );
};

export default AppNavigation;
