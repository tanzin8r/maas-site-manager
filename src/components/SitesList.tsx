import { useQuery } from "react-query";
import "./SitesList.scss";

type Site = {
  name: string;
  url: string; // <full URL including protocol>,
  connection: "stable" | "stale" | "lost";
  last_seen: string; // <ISO 8601 date>,
  address: {
    countrycode: string; // <alpha2 country code>,
    city: string;
    zip: string;
    street: string;
  };
  timezone: string; // <three letter abbreviation>,
  stats: {
    machines: number;
    occupied_machines: number;
    ready_machines: number;
    error_machines: number;
  };
};

type Sites = {
  items: Site[];
  total: number;
  page: number;
  size: number;
};

const SiteRow = ({ site }: { site: Site }) => {
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

const SitesList = () => {
  const query = useQuery<Sites>("/sites", async function () {
    const response = await fetch("/sites");
    if (!response.ok) {
      throw new Error("Network response was not ok");
    }
    const responseJson = await response.json();
    return responseJson;
  });

  return (
    <div>
      <h2>Sites</h2>
      <table>
        <thead>
          <tr>
            <th>
              <div>MAAS region alias</div>
              <div>URL</div>
            </th>
            <th>
              <div>connection</div>
              <div>last seen</div>
            </th>
            <th>
              <div>country</div>
              <div>street, city, zip</div>
            </th>
            <th>
              <div>local time</div>
              <div>timezone</div>
            </th>
            <th>
              <div>total number of machines</div>
              <div>machines per aggregated status</div>
            </th>
          </tr>
        </thead>
        <tbody>
          {query.data
            ? query.data.items.map((site) => <SiteRow site={site} />)
            : null}
        </tbody>
      </table>
    </div>
  );
};

export default SitesList;
