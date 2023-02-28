import type { Site } from "../types";

const SiteRow: React.FC<{ site: Site }> = ({ site }: { site: Site }) => {
  return (
    <tr>
      <td>
        <div>{site.name}</div>
        <div>
          <a href={site.url}>{site.url}</a>
        </div>
      </td>
      <td>
        <div>{site.connection}</div>
        <div>{site.last_seen}</div>
      </td>
      <td>
        <div>{site.address.countrycode}</div>
        <div>
          {site.address.street}, {site.address.city}, {site.address.zip}
        </div>
      </td>
      <td>
        <div>11:00 (local time)</div>
        <div>{site.timezone}</div>
      </td>
      <td>
        <div>{site.stats.machines}</div>
        <div>
          Ready: {site.stats.ready_machines}, Occupied:
          {site.stats.occupied_machines}, Error: {site.stats.error_machines}
        </div>
      </td>
    </tr>
  );
};

export default SiteRow;
