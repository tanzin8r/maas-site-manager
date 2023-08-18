/* eslint-disable no-restricted-imports */
import { Link } from "@canonical/react-components";
import type { LinkProps } from "react-router-dom";

const ExternalLink = ({ children, to, ...props }: LinkProps & { to: string }) => (
  <Link {...props} href={to} rel="noreferrer noopener" target="_blank">
    {children}
  </Link>
);

export default ExternalLink;
