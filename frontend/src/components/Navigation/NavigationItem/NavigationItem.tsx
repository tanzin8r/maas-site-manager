import { useId } from "react";

import { Icon } from "@canonical/react-components";
import { Link } from "react-router-dom";

import type { NavLink } from "@/components/Navigation/types";
import { isSelected } from "@/components/Navigation/utils";

type Props = {
  navLink: NavLink;
  path: string;
};

const NavigationItem = ({ navLink, path }: Props): JSX.Element => {
  const id = useId();
  return (
    <li
      aria-labelledby={`${navLink.label}-${id}`}
      className={`p-side-navigation__item${isSelected(path, navLink) ? " is-selected" : ""}`}
    >
      <Link
        aria-current={!navLink.external && isSelected(path, navLink) ? "page" : undefined}
        className="p-side-navigation__link"
        id={`${navLink.label}-${id}`}
        onClick={(event) => {
          // removing the focus from the link element after click
          // this allows the side navigation to collapse on mouseleave
          event.currentTarget.blur();
        }}
        rel={navLink.external ? "noreferrer noopener" : ""}
        target={navLink.external ? "_blank" : ""}
        to={navLink.url}
      >
        {navLink.icon ? (
          typeof navLink.icon === "string" ? (
            <Icon className="p-side-navigation__icon" light name={navLink.icon} />
          ) : (
            <>{navLink.icon}</>
          )
        ) : null}
        <span className="p-side-navigation__label">{navLink.label}</span>
      </Link>
    </li>
  );
};

export default NavigationItem;
