import { useId, useMemo } from "react";

import { Icon } from "@canonical/react-components";
import classNames from "classnames";

import NavigationItem from "@/components/Navigation/NavigationItem/NavigationItem";
import type { NavGroup, NavItem } from "@/components/Navigation/types";
import { isNavGroup, isSelected } from "@/components/Navigation/utils";
import type { RoutePath } from "@/config/routes";

type Props = {
  hideDivider?: boolean;
  isDark?: boolean;
  hasIcons?: boolean;
  items: NavItem[];
  path: RoutePath;
  onClick: () => void;
};

const NavigationItemGroup = ({ group, path, onClick }: { group: NavGroup } & Pick<Props, "path" | "onClick">) => {
  const id = useId();
  const hasActiveChild = useMemo(() => {
    for (const navLink of group.navLinks) {
      if (isSelected(path, navLink)) {
        return true;
      }
    }
    return false;
  }, [group, path]);

  return (
    <>
      <li className={classNames("p-side-navigation__item", { "has-active-child": hasActiveChild })}>
        <span className="p-side-navigation__text" key={`${group.groupTitle}-${id}`}>
          {group.groupIcon ? (
            typeof group.groupIcon === "string" ? (
              <Icon className="p-side-navigation__icon" light name={group.groupIcon} />
            ) : (
              <>{group.groupIcon}</>
            )
          ) : null}
          <div className="p-side-navigation__label p-heading--small" id={`${group.groupTitle}-${id}`}>
            {group.groupTitle}
          </div>
        </span>
        <ul aria-labelledby={`${group.groupTitle}-${id}`} className="p-side-navigation__list">
          {group.navLinks.map((navLink, i) => (
            <NavigationItem key={i} navLink={navLink} onClick={onClick} path={path} />
          ))}
        </ul>
      </li>
    </>
  );
};

const NavigationList = ({ hideDivider = false, items, path, isDark, hasIcons, onClick }: Props): JSX.Element => {
  return (
    <div className={classNames({ "is-dark": isDark, "p-side-navigation--icons": hasIcons })}>
      <ul className={classNames("p-side-navigation__list", { "no-divider": hideDivider })}>
        {items.map((item, i) => {
          if (isNavGroup(item)) {
            return <NavigationItemGroup group={item} key={`${i}-${item.groupTitle}`} onClick={onClick} path={path} />;
          } else return <NavigationItem key={`${i}-${item.label}`} navLink={item} onClick={onClick} path={path} />;
        })}
      </ul>
    </div>
  );
};

export default NavigationList;
