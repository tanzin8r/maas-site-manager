import SiteSelectionTable from "./SiteSelectionTable";

import type { Site } from "@/api/types";

type Props = {
  selectedSites: Site[];
};

const SiteSelection = ({ selectedSites }: Props) => {
  return (
    <div className="u-padding-top--medium">
      <h3 className="p-heading--4 u-no-padding--top u-no-margin">Selection</h3>
      {selectedSites.length > 0 && (
        <p>
          {selectedSites.length} selected <button className="p-button--link">clear selection</button>
        </p>
      )}
      <SiteSelectionTable selectedSites={selectedSites} />
    </div>
  );
};

export default SiteSelection;
