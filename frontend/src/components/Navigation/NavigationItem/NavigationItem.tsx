import { useId } from "react";

import { Icon } from "@canonical/react-components";

import type { RoutePath } from "@/base/routesConfig";
import ExternalLink from "@/components/ExternalLink/ExternalLink";
import type { NavLink } from "@/components/Navigation/types";
import { isSelected } from "@/components/Navigation/utils";
import { Link } from "@/router";

type Props = {
  navLink: NavLink;
  path: RoutePath;
  onClick: () => void;
};

const LinkContent = ({ navLink }: { navLink: NavLink }) => (
  <>
    {navLink.icon ? (
      typeof navLink.icon === "string" ? (
        <Icon className="p-side-navigation__icon" light name={navLink.icon} />
      ) : (
        <>{navLink.icon}</>
      )
    ) : null}
    <span className="p-side-navigation__label">{navLink.label}</span>
  </>
);

const NavigationItem = ({ navLink, path, onClick }: Props): JSX.Element => {
  const id = useId();
  const linkProps = {
    className: "p-side-navigation__link",
    id: `${navLink.label}-${id}`,
    onClick: (event: React.MouseEvent<HTMLAnchorElement, MouseEvent>) => {
      onClick();
      // removing the focus from the link element after click
      // this allows the side navigation to collapse on mouseleave
      event.currentTarget.blur();
    },
  };

  return (
    <li
      aria-labelledby={`${navLink.label}-${id}`}
      className={`p-side-navigation__item${isSelected(path, navLink) ? " is-selected" : ""}`}
    >
      {!navLink.external ? (
        <Link {...linkProps} aria-current={isSelected(path, navLink) ? "page" : undefined} to={navLink.url}>
          <LinkContent navLink={navLink} />
        </Link>
      ) : (
        <ExternalLink {...linkProps} to={navLink.url}>
          <LinkContent navLink={navLink} />
        </ExternalLink>
      )}
    </li>
  );
};

export default NavigationItem;
