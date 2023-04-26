import classNames from "classnames";
import get from "lodash/get";

import type { Stats } from "@/api/types";
import docsUrls from "@/base/docsUrls";
import ExternalLink from "@/components/ExternalLink";
import TooltipButton from "@/components/base/TooltipButton";
import { formatDistanceToNow } from "@/utils";

export const connectionIcons: Record<Stats["connection"], string> = {
  stable: "is-stable",
  lost: "is-lost",
  unknown: "is-unknown",
} as const;
export const connectionLabels: Record<Stats["connection"], string> = {
  stable: "Stable",
  lost: "Lost",
  unknown: "Waiting for first",
} as const;

type ConnectionInfoProps = { connection: Stats["connection"]; lastSeen?: Stats["last_seen"] };

const getLastSeenText = ({ connection, lastSeen }: ConnectionInfoProps) => {
  if (!lastSeen) {
    return null;
  }
  return connection === "unknown" ? `heartbeat since ${formatDistanceToNow(lastSeen)}` : formatDistanceToNow(lastSeen);
};

const ConnectionInfo = ({ connection, lastSeen }: ConnectionInfoProps) => {
  return (
    <>
      <TooltipButton
        iconName=""
        message={
          connection === "unknown" ? (
            "Haven't received a heartbeat from this region yet"
          ) : connection === "stable" ? (
            "Received a heartbeat in the expected interval of 5 minutes"
          ) : (
            <>
              Haven't received a heartbeat in the expected interval of 5 minutes.
              <br />
              <ExternalLink to={docsUrls.troubleshooting}>
                Check the documentation for troubleshooting steps.
              </ExternalLink>
            </>
          )
        }
        position="btm-center"
      >
        <div className={classNames("connection__text", "status-icon", get(connectionIcons, connection))}>
          {get(connectionLabels, connection)}
        </div>
      </TooltipButton>
      <div className="connection__text u-text--muted">
        <time dateTime={lastSeen}>{getLastSeenText({ connection, lastSeen })}</time>
      </div>
    </>
  );
};

export default ConnectionInfo;
