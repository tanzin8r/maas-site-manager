import { Spinner, Notification, Button, Icon } from "@canonical/react-components";
import classNames from "classnames";
import { get } from "lodash";

import ErrorMessage from "@/components/ErrorMessage";
import ExternalLink from "@/components/ExternalLink/ExternalLink";
import {
  connectionIcons,
  connectionLabels,
  getLastSeenText,
} from "@/components/SitesList/SitesTable/ConnectionInfo/ConnectionInfo";
import LocalTime from "@/components/base/LocalTime/LocalTime";
import RemoveButton from "@/components/base/RemoveButton";
import { useAppLayoutContext, useRowSelectionContext } from "@/context";
import { useRegionDetailsContext } from "@/context/RegionDetailsContext";
import { useSiteQuery } from "@/hooks/react-query";
import { getCountryName } from "@/utils";

const RegionDetails = () => {
  const { regionId } = useRegionDetailsContext();
  const { data: site, error, isLoading } = useSiteQuery(regionId);
  const { setSidebar } = useAppLayoutContext();
  const { setRowSelection } = useRowSelectionContext("sites");
  const stats = site?.stats;

  return (
    <div className="region-details">
      <Button
        appearance="base"
        aria-label="Close"
        className="region-details__close-button"
        hasIcon
        onClick={() => setSidebar(null)}
      >
        <Icon name="close" />
      </Button>
      {error ? (
        <Notification severity="negative" title="Error">
          <ErrorMessage error={error} />
        </Notification>
      ) : stats && site && !isLoading ? (
        <>
          <h3 className="p-heading--4 region-details__name">{site.name}</h3>
          <ExternalLink to={site.url}>{site.url}</ExternalLink>
          <table className="region-details__table">
            <tbody>
              <tr>
                <td className="u-text--muted region-details__table-row-label">Status</td>
                <td
                  className={classNames(
                    "region-details__table-item",
                    "connection__text",
                    "status-icon",
                    { "u-text--muted": site.connection_status === "unknown" },
                    get(connectionIcons, site.connection_status),
                  )}
                >
                  {get(connectionLabels, site.connection_status)}
                  <span className="u-text--muted region-details__last-seen">
                    {getLastSeenText({ connection: site.connection_status, lastSeen: stats.last_seen })}
                  </span>
                </td>
              </tr>
              <tr>
                <td className="u-text--muted region-details__table-row-label">Country</td>
                <td className="region-details__table-item">{getCountryName(site.country)}</td>
              </tr>
              <tr>
                <td className="u-text--muted region-details__table-row-label">Street</td>
                <td className="region-details__table-item">{site.street}</td>
              </tr>
              <tr>
                <td className="u-text--muted region-details__table-row-label">City</td>
                <td className="region-details__table-item">{site.city}</td>
              </tr>
              <tr>
                <td className="u-text--muted region-details__table-row-label">Zip</td>
                <td className="region-details__table-item">{site.zip}</td>
              </tr>
              <tr>
                <td className="u-text--muted region-details__table-row-label">Local time</td>
                <td className="region-details__table-item">
                  <LocalTime timezone={site.timezone} />
                </td>
              </tr>
              <tr>
                <td className="u-text--muted region-details__table-row-label">Machines</td>
                <td className="region-details__table-item">{stats.total_machines}</td>
              </tr>
              <tr>
                <td className="u-text--muted region-details__table-row-label">Machines status</td>
                <td className="region-details__table-item">
                  <span className="region-details__machines-statuses">
                    <i className="p-icon--status-deployed"></i>
                    <span className="region-details__machines-status-count" data-testid="deployed-machines">
                      {stats.deployed_machines}
                    </span>
                    <span>Deployed</span>

                    <i className="p-icon--status-allocated"></i>
                    <span className="region-details__machines-status-count" data-testid="allocated-machines">
                      {stats.allocated_machines}
                    </span>
                    <span>Allocated</span>

                    <i className="p-icon--status-ready"></i>
                    <span className="region-details__machines-status-count" data-testid="ready-machines">
                      {stats.ready_machines}
                    </span>
                    <span>Ready / New</span>

                    <span></span>
                    <span className="region-details__machines-status-count" data-testid="error-machines">
                      {stats.error_machines}
                    </span>
                    <span>Error</span>
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
          <hr />
          <span className="u-flex u-flex--justify-end">
            <Button appearance="base" onClick={() => setSidebar("editRegion")}>
              <Icon name="edit" /> Edit
            </Button>
            <RemoveButton
              onClick={() => {
                setRowSelection({ [site.id]: true });
                setSidebar("removeRegions");
              }}
              showDeleteIcon
            />
          </span>
        </>
      ) : (
        <Spinner />
      )}
    </div>
  );
};

export default RegionDetails;
