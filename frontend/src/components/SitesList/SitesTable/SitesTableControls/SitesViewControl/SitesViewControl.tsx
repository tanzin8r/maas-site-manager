import { Button, Icon } from "@canonical/react-components";

import { Link, useLocation } from "@/utils/router";

const SitesViewControl = () => {
  const { pathname } = useLocation();
  return (
    <div className="p-segmented-control">
      <div aria-label="sites view control" className="p-segmented-control__list sites-view-control" role="tablist">
        <Button
          aria-selected={pathname === "/sites/map"}
          className="p-segmented-control__button"
          element={Link}
          id="map"
          role="tab"
          to="/sites/map"
        >
          <Icon name="exposed" />
          <span>Map</span>
        </Button>
        <Button
          aria-selected={pathname === "/sites/list"}
          className="p-segmented-control__button"
          element={Link}
          id="table"
          role="tab"
          to="/sites/list"
        >
          <Icon name="switcher-environments" />
          <span>Table</span>
        </Button>
      </div>
    </div>
  );
};

export default SitesViewControl;
