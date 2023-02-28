import React from "react";

import { useQuery } from "react-query";

import SiteRow from "./components/SiteRow";
import "./SitesList.scss";
import type { Sites } from "./types";

const SitesList: React.FC = () => {
  const query = useQuery<Sites>("/api/sites", async function () {
    const response = await fetch("/api/sites");
    if (!response.ok) {
      throw new Error("Network response was not ok");
    }
    const responseJson = await response.json();
    return responseJson;
  });

  return (
    <div>
      <h2>{query?.data?.items?.length || ""} MAAS Regions</h2>
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
        <tbody>{query.data ? query.data.items.map((site) => <SiteRow key={site.url} site={site} />) : null}</tbody>
      </table>
    </div>
  );
};

export default SitesList;
