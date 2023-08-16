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
import { useAppLayoutContext } from "@/context";
import { useSiteDetailsContext } from "@/context/SiteDetailsContext";
import { useSiteQuery } from "@/hooks/react-query";

const SiteSummary = ({ id }: { id: Site["id"] }) => {
  const { data: site, error, isLoading } = useSiteQuery({ id });
  const { setSidebar } = useAppLayoutContext();
  const { setSelected: setSiteId } = useSiteDetailsContext();
  const stats = site?.stats;

  return (
    <Card className="site-summary" title="Site details">
      {error ? (
        <Notification severity="negative" title="Error while fetching site">
          <ErrorMessage error={error} />
        </Notification>
      ) : site ? (
        <>
          <div>
            <span className="site-summary__header">
              <h4 className="site-summary__name">{site.name}</h4>
              <Button
                appearance="base"
                className="site-summary__button--edit"
                onClick={() => {
                  setSiteId(id);
                  setSidebar("editSite");
                }}
              >
                <Icon name="edit" /> Edit
              </Button>
            </span>
            <ExternalLink to={site.url}>{site.url}</ExternalLink>
          </div>
          <table className="site-summary__table">
            <tbody>
              <tr>
                <td className="u-text--muted site-summary__table-item">Status</td>
                <td
                  className={classNames(
                    "connection__text",
                    "status-icon",
                    get(connectionIcons, site.connection_status),
                  )}
                >
                  {get(connectionLabels, site.connection_status)}
                  <span className="u-text--muted site-summary__last-seen">
                    {stats
                      ? getLastSeenText({
                          lastSeen: stats.last_seen,
                          connection: site.connection_status,
                          format: "long",
                        })
                      : null}
                  </span>
                </td>
              </tr>
              <tr>
                <td className="u-text--muted site-summary__table-item">Machines</td>
                <td>{stats?.total_machines}</td>
              </tr>
              <tr>
                <td className="u-text--muted site-summary__table-item">Machine status</td>
                <td>{stats ? <AggregatedStatus hideLabel stats={stats} /> : null}</td>
              </tr>
            </tbody>
          </table>
        </>
      ) : isLoading ? (
        <Spinner />
      ) : null}
    </Card>
  );
};

export default SiteSummary;
