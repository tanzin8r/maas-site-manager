import { Button } from "@canonical/react-components";
import classNames from "classnames";
import { useLocation } from "react-router-dom";
import useLocalStorageState from "use-local-storage-state";

import NavigationBanner from "./NavigationBanner";
import NavigationCollapseToggle from "./NavigationCollapseToggle";
import NavigationList from "./NavigationList";
import type { NavLink } from "./types";

export const navItems: NavLink[] = [
  {
    label: "Regions",
    url: "/sites",
    icon: "maas",
  },
];

export const navItemsBottom: NavLink[] = [
  {
    label: "Settings",
    url: "/settings",
    icon: "settings",
  },
];

const navItemsAccount = [{ label: "Log out", url: "/logout" }];

const Navigation = (): JSX.Element => {
  const [isCollapsed, setIsCollapsed] = useLocalStorageState<boolean>("appSideNavIsCollapsed", { defaultValue: true });
  const location = useLocation();
  const path = location.pathname;

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
        className={classNames("l-navigation", { "is-collapsed": isCollapsed, "is-pinned": !isCollapsed })}
      >
        <div className="l-navigation__drawer">
          <div className="p-panel is-dark">
            <div className="p-panel__header is-sticky">
              <NavigationBanner>
                <div className="l-navigation__controls">
                  <NavigationCollapseToggle isCollapsed={isCollapsed} setIsCollapsed={setIsCollapsed} />
                </div>
              </NavigationBanner>
            </div>
            <div className="p-panel__content">
              <NavigationList hasIcons isDark items={navItems} path={path} />
              <NavigationList hasIcons isDark items={navItemsBottom} path={path} />
              <NavigationList hasIcons isDark items={navItemsAccount} path={path} />
            </div>
          </div>
        </div>
      </nav>
    </>
  );
};

export default Navigation;
