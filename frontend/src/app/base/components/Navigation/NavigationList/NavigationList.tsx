import type { ReactElement } from "react";
import { useId, useMemo } from "react";

import { Navigation } from "@canonical/maas-react-components";
import classNames from "classnames";

import NavigationItem from "@/app/base/components/Navigation/NavigationItem/NavigationItem";
import type { NavGroup, NavItem } from "@/app/base/components/Navigation/types";
import { isNavGroup, isSelected } from "@/app/base/components/Navigation/utils";
import type { RoutePath } from "@/app/base/routes";

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
      <Navigation.Item hasActiveChild={hasActiveChild}>
        <Navigation.Text key={`${group.groupTitle}-${id}`}>
          {group.groupIcon ? <Navigation.Icon name={group.groupIcon} /> : null}
          <Navigation.Label id={`${group.groupTitle}-${id}`} variant="group">
            {group.groupTitle}
          </Navigation.Label>
        </Navigation.Text>
        <Navigation.List aria-labelledby={`${group.groupTitle}-${id}`}>
          {group.navLinks.map((navLink, i) => (
            <NavigationItem key={i} navLink={navLink} onClick={onClick} path={path} />
          ))}
        </Navigation.List>
      </Navigation.Item>
    </>
  );
};

const NavigationList = ({ hideDivider = false, items, path, onClick }: Props): ReactElement => {
  return (
    <Navigation.List className={classNames({ "no-divider": hideDivider })}>
      {items.map((item, i) => {
        if (isNavGroup(item)) {
          return <NavigationItemGroup group={item} key={`${i}-${item.groupTitle}`} onClick={onClick} path={path} />;
        } else return <NavigationItem key={`${i}-${item.label}`} navLink={item} onClick={onClick} path={path} />;
      })}
    </Navigation.List>
  );
};

export default NavigationList;
