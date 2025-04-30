import { Icon } from "@canonical/react-components";
import type { Header } from "@tanstack/react-table";

import type { Image } from "@/api";
import type { Site, User } from "@/apiclient";

export const SortIndicator = ({
  header,
}: {
  header: Header<User, Partial<User>> | Header<Site, Partial<Site>> | Header<Image, Partial<Image>>;
}) =>
  ({
    asc: <Icon name="chevron-up">ascending</Icon>,
    desc: <Icon name="chevron-down">descending</Icon>,
  })[header?.column?.getIsSorted() as string] ?? null;

export default SortIndicator;
