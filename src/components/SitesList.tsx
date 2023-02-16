import { useQuery } from "react-query";
import "./SitesList.scss";

type Site = {
  name: string;
  url: string;
  connection: "stable" | "stale" | "lost";
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
      <td>{site.name}</td>
      <td>{site.url}</td>
      <td>{site.connection}</td>
      <td>{site.address.countrycode}</td>
      <td>{site.address.city}</td>
      <td>{site.address.zip}</td>
      <td>{site.address.street}</td>
      <td>{site.timezone}</td>
      <td>{site.stats.machines}</td>
      <td>{site.stats.occupied_machines}</td>
      <td>{site.stats.ready_machines}</td>
      <td>{site.stats.error_machines}</td>
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
