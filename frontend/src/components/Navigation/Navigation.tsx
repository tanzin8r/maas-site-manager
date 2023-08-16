import { Button } from "@canonical/react-components";
import classNames from "classnames";
import useLocalStorageState from "use-local-storage-state";

import NavigationBanner from "./NavigationBanner";
import NavigationCollapseToggle from "./NavigationCollapseToggle";
import NavigationList from "./NavigationList";
import type { ExternalNavLink, LocalNavLink } from "./types";

import BREAKPOINTS from "@/config/breakpoints";
import type { RoutePath } from "@/config/routes";
import { useCurrentUserQuery } from "@/hooks/react-query";
import { useLocation } from "@/utils/router";

export const navItems: LocalNavLink[] = [
  {
    label: "Sites",
    url: "/sites",
    icon: "machines",
  },
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
  { external: true, icon: "submit-bug", label: "Report a bug", url: "" }, // TODO: Replace this with actual link once known
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

const Navigation = ({ isLoggedIn }: NavProps): JSX.Element => {
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

  return (
    <>
      <header aria-label="navigation" className="l-navigation-bar">
        <div className="p-panel is-dark">
          <div className="p-panel__header">
            <NavigationBanner />
            <div className="p-panel__controls u-nudge-down--small u-no-margin-top">
              <Button
                appearance="base"
                className="has-icon is-dark"
                onClick={() => {
                  setIsCollapsed(!isCollapsed);
                }}
              >
                Menu
              </Button>
            </div>
          </div>
        </div>
      </header>
      <nav
        aria-label="main"
        className={classNames("l-navigation", {
          "is-collapsed": isCollapsed,
          "is-pinned": !isCollapsed,
        })}
      >
        <div className="l-navigation__drawer">
          <div className="p-panel is-dark u-flex u-flex--column u-flex--justify-between">
            <span>
              <div className="p-panel__header is-sticky">
                <NavigationBanner>
                  <div className="l-navigation__controls">
                    <NavigationCollapseToggle isCollapsed={isCollapsed} setIsCollapsed={setIsCollapsed} />
                    <Button
                      appearance="base"
                      className="is-dark b-btn-transparent u-hide u-no-wrap u-show--small"
                      onClick={(e) => {
                        setIsCollapsed(!isCollapsed);
                        // Make sure the button does not have focus
                        // .l-navigation remains open with :focus-within
                        e.stopPropagation();
                        e.currentTarget.blur();
                      }}
                    >
                      Close menu
                    </Button>
                  </div>
                </NavigationBanner>
              </div>
              {isLoggedIn && (
                <div className="p-panel__content">
                  <NavigationList hasIcons isDark items={navItems} onClick={handleNavlinkClick} path={path} />
                  <NavigationList hasIcons isDark items={settingsNavItems} onClick={handleNavlinkClick} path={path} />
                  <AccountNavigationList handleNavlinkClick={handleNavlinkClick} path={path} />
                </div>
              )}
            </span>
            <NavigationList
              hasIcons
              hideDivider
              isDark
              items={navItemsBottom}
              onClick={handleNavlinkClick}
              path={path}
            />
          </div>
        </div>
      </nav>
    </>
  );
};

export default Navigation;
