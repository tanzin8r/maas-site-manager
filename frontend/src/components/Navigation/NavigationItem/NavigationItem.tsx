import type { ReactElement } from "react";
import { useId } from "react";

import { ExternalLink, Navigation } from "@canonical/maas-react-components";

import type { NavLink } from "@/components/Navigation/types";
import { isSelected } from "@/components/Navigation/utils";
import type { RoutePath } from "@/config/routes";
import { Link } from "@/utils/router";

type Props = {
  navLink: NavLink;
  path: RoutePath;
  onClick: () => void;
};

const LinkContent = ({ navLink }: { navLink: NavLink }) => (
  <>
    {navLink.icon ? <Navigation.Icon light name={navLink.icon} /> : null}
    <Navigation.Label>{navLink.label}</Navigation.Label>
  </>
);

const NavigationItem = ({ navLink, path, onClick }: Props): ReactElement => {
  const id = useId();
  const linkProps = {
    id: `${navLink.label}-${id}`,
    onClick: (event: React.MouseEvent<HTMLAnchorElement, MouseEvent>) => {
      onClick();
      // removing the focus from the link element after click
      // this allows the side navigation to collapse on mouseleave
      event.currentTarget.blur();
    },
  };

  return (
    <Navigation.Item aria-labelledby={`${navLink.label}-${id}`}>
      <Navigation.Link
        aria-current={isSelected(path, navLink) ? "page" : undefined}
        as={navLink.external ? ExternalLink : Link}
        to={navLink.url}
        {...linkProps}
      >
        <LinkContent navLink={navLink} />
      </Navigation.Link>
    </Navigation.Item>
  );
};

export default NavigationItem;
