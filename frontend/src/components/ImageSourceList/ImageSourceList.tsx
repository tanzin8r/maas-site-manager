import { ContentSection, MainToolbar } from "@canonical/maas-react-components";
import { Button } from "@canonical/react-components";

import ImageSourceListTable from "./ImageSourceListTable";
import type { BootSource } from "./types";

export const fakeBootSources: { items: BootSource[] } = {
  items: [
    {
      id: 1,
      url: "custom",
      keyring: "",
      sync_interval: 0,
      priority: 1,
      status: "connected",
      total_images: 100,
    },
    {
      id: 1,
      url: "images.maas.io",
      keyring: "abcdefghijklmnopqrstuvwxyz",
      sync_interval: 300,
      priority: 1,
      status: "connected",
      total_images: 100,
    },
    {
      id: 1,
      url: "somewhere-else.long-domain-name.abc.xyz",
      keyring: "abcdefghijklmnopqrstuvwxyz",
      sync_interval: 150,
      priority: 1,
      status: "unreachable",
      total_images: 100,
    },
    {
      id: 1,
      url: "another-really-long-name.a-domain-somewhere.abc.xyz",
      keyring: "abcdefghijklmnopqrstuvwxyz",
      sync_interval: 0,
      priority: 1,
      status: "gpg_error",
      total_images: 100,
    },
  ],
};

const ImageSourceList = () => {
  return (
    <ContentSection>
      <ContentSection.Header>
        <MainToolbar>
          <MainToolbar.Title>Source</MainToolbar.Title>
          <MainToolbar.Controls>
            <Button appearance="positive">Add image source</Button>
          </MainToolbar.Controls>
        </MainToolbar>
      </ContentSection.Header>
      <ContentSection.Content>
        <ImageSourceListTable data={fakeBootSources} error={null} isPending={false} />
      </ContentSection.Content>
    </ContentSection>
  );
};

export default ImageSourceList;
