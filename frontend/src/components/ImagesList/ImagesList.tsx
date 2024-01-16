import { ContentSection, ExternalLink, MainToolbar } from "@canonical/maas-react-components";
import { Button } from "@canonical/react-components";

import RemoveButton from "@/components/base/RemoveButton";
import { useAppLayoutContext } from "@/context";
import { useImagesQuery } from "@/hooks/react-query";

const ImagesList = () => {
  const isActionDisabled = false;
  const { setSidebar } = useAppLayoutContext();

  // TODO: remove once https://warthogs.atlassian.net/browse/MAASENG-2566 is complete
  useImagesQuery({ page: 1, size: 10 });

  return (
    <ContentSection>
      <MainToolbar>
        <MainToolbar.Title>Images</MainToolbar.Title>
        <MainToolbar.Controls>
          <RemoveButton
            disabled={isActionDisabled}
            label="Delete"
            onClick={() => setSidebar("deleteImages")}
            type="button"
          />
          <Button onClick={() => setSidebar("downloadImages")} type="button">
            Download images
          </Button>
          <Button onClick={() => setSidebar("uploadImage")} type="button">
            Upload Image
          </Button>
        </MainToolbar.Controls>
      </MainToolbar>
      <p>
        <ExternalLink to="https://warthogs.atlassian.net/browse/MAASENG-2566">
          TODO: complete images table implementation
        </ExternalLink>
      </p>
    </ContentSection>
  );
};

export default ImagesList;
