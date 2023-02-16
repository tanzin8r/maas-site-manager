import { useQuery } from "react-query";
import "./SitesList.scss";

type Sites = {
  items: {
    name: string;
  }[];
  total: number;
  page: number;
  size: number;
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
      {query.data
        ? query.data.items.map((site) => <div key={site.name}>{site.name}</div>)
        : null}
    </div>
  );
};

export default SitesList;
