import { Icon } from "@canonical/react-components";
import type { Header } from "@tanstack/react-table";

import type { Site, User } from "@/api/types";

export const SortIndicator = ({ header }: { header: Header<User, Partial<User>> | Header<Site, Partial<Site>> }) =>
  ({
    asc: <Icon aria-label="ascending" name="chevron-up" />,
    desc: <Icon aria-label="descending" name="chevron-down" />,
  })[header?.column?.getIsSorted() as string] ?? null;

export default SortIndicator;
