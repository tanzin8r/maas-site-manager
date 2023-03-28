import classNames from "classnames";
import get from "lodash/get";

import type { Site } from "@/api/types";

export const connectionIcons: Record<Site["connection"], string> = {
  stable: "is-stable",
  lost: "is-lost",
  unknown: "is-unknown",
} as const;
export const connectionLabels: Record<Site["connection"], string> = {
  stable: "Stable",
  lost: "Lost",
  unknown: "Waiting for first",
} as const;

type ConnectionInfoProps = { connection: Site["connection"]; lastSeen?: Site["last_seen"] };

const ConnectionInfo = ({ connection, lastSeen }: ConnectionInfoProps) => (
  <>
    <div className={classNames("connection__text", "status-icon", get(connectionIcons, connection))}>
      {get(connectionLabels, connection)}
    </div>
    <div className="connection__text u-text--muted">{lastSeen}</div>
  </>
);
export default ConnectionInfo;
