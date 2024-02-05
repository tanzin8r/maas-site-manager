import { MainToolbar, ContentSection } from "@canonical/maas-react-components";
import { Button } from "@canonical/react-components";
import type { ColumnDef, Column } from "@tanstack/react-table";

import ImagesTable from "./ImagesTable";

import type { Image } from "@/api";
import RemoveButton from "@/components/base/RemoveButton";
import { useAppLayoutContext, useRowSelection } from "@/context";

export type ImageColumnDef = ColumnDef<Image, Partial<Image>>;
export type ImageColumn = Column<Image, unknown>;

const ImagesList = ({
  isDeleteDisabled,
  setSidebar,
}: {
  isDeleteDisabled: boolean;
  setSidebar: ReturnType<typeof useAppLayoutContext>["setSidebar"];
}) => {
  return (
    <ContentSection>
      <ContentSection.Header>
        <MainToolbar>
          <MainToolbar.Title>Images</MainToolbar.Title>
          <MainToolbar.Controls>
            <RemoveButton
              disabled={isDeleteDisabled}
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
      </ContentSection.Header>
      <ContentSection.Content>
        <ImagesTable />
      </ContentSection.Content>
    </ContentSection>
  );
};

const ImagesListContainer = () => {
  const { rowSelection } = useRowSelection("images");
  const isDeleteDisabled = Object.keys(rowSelection).length <= 0;
  const { setSidebar } = useAppLayoutContext();

  return <ImagesList isDeleteDisabled={isDeleteDisabled} setSidebar={setSidebar} />;
};

export default ImagesListContainer;
