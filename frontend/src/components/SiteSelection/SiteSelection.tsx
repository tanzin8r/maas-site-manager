import { ContentSection } from "@canonical/maas-react-components";

import SiteSelectionTable from "./SiteSelectionTable";

import type { Site } from "@/api/types";

type Props = {
  selectedSites: Site[];
};

const SiteSelection = ({ selectedSites }: Props) => {
  return (
    <ContentSection>
      <ContentSection.Title>Selection</ContentSection.Title>
      <ContentSection.Content>
        {selectedSites.length > 0 && (
          <p>
            {selectedSites.length} selected <button className="p-button--link">clear selection</button>
          </p>
        )}
        <SiteSelectionTable selectedSites={selectedSites} />
      </ContentSection.Content>
    </ContentSection>
  );
};

export default SiteSelection;
