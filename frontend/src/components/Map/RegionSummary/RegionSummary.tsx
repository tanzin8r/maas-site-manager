import { Button, Card, Icon, Notification, Spinner } from "@canonical/react-components";
import classNames from "classnames";
import { get } from "lodash";

import type { Site } from "@/api/types";
import ErrorMessage from "@/components/ErrorMessage/ErrorMessage";
import ExternalLink from "@/components/ExternalLink/ExternalLink";
import AggregatedStatus from "@/components/SitesList/SitesTable/AggregatedStatus/AggregatedStatus";
import {
  connectionIcons,
  connectionLabels,
  getLastSeenText,
} from "@/components/SitesList/SitesTable/ConnectionInfo/ConnectionInfo";
import { useSiteQuery } from "@/hooks/react-query";

const RegionSummary = ({ id }: { id: Site["id"] }) => {
  const { data: site, error, isLoading } = useSiteQuery(id);
  const stats = site?.stats;

  return (
    <Card className="region-summary" title="Region details">
      {!stats || !site || isLoading ? (
        <Spinner />
      ) : error ? (
        <Notification severity="negative" title="Error while fetching site">
          <ErrorMessage error={error} />
        </Notification>
      ) : (
        <>
          <div>
            <span className="region-summary__header">
              <h4 className="region-summary__name">{site.name}</h4>
              <Button appearance="base" className="region-summary__button--edit">
                <Icon name="edit" /> Edit
              </Button>
            </span>
            <ExternalLink to={site.url}>{site.url}</ExternalLink>
          </div>
          <table className="region-summary__table">
            <tbody>
              <tr>
                <td className="u-text--muted region-summary__table-item">Status</td>
                <td
                  className={classNames(
                    "connection__text",
                    "status-icon",
                    get(connectionIcons, site.connection_status),
                  )}
                >
                  {get(connectionLabels, site.connection_status)}
                  <span className="u-text--muted region-summary__last-seen">
                    last seen {getLastSeenText({ connection: site.connection_status, lastSeen: stats.last_seen })}
                  </span>
                </td>
              </tr>
              <tr>
                <td className="u-text--muted region-summary__table-item">Machines</td>
                <td>{stats.total_machines}</td>
              </tr>
              <tr>
                <td className="u-text--muted region-summary__table-item">Machine status</td>
                <td>
                  <AggregatedStatus hideLabel stats={stats} />
                </td>
              </tr>
            </tbody>
          </table>
        </>
      )}
    </Card>
  );
};

export default RegionSummary;
