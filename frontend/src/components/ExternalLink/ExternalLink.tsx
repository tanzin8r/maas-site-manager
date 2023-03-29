import type { LinkProps } from "react-router-dom";
import { Link } from "react-router-dom";

const ExternalLink = ({ to, children }: LinkProps) => (
  <Link rel="noreferrer noopener" target="_blank" to={to}>
    {children}
  </Link>
);

export default ExternalLink;
