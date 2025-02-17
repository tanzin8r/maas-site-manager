import { ActionButton, Button } from "@canonical/react-components";

import { fakeBootSources } from "../ImageSourceList/ImageSourceList";

import { useAppLayoutContext } from "@/context";
import { useBootSourceContext } from "@/context/BootSourceContext";

const DeleteImageSource = () => {
  const { selected: id } = useBootSourceContext();
  const { setSidebar } = useAppLayoutContext();

  // TODO: Replace with API call when ready https://warthogs.atlassian.net/browse/MAASENG-4439
  const bootSource = fakeBootSources.items.find((bootSource) => bootSource.id === id);

  return (
    <div>
      <h3 className="p-heading--4">Remove {bootSource?.url}?</h3>
      <p>Are you sure you want to remove {bootSource?.url} as an image source in MAAS Site Manager?</p>
      <p>
        Removing an image source will remove all images that were pulled from this source in MAAS Site Manager and all
        connected MAAS sites.
      </p>
      <hr />
      <div className="u-flex u-flex--justify-end u-padding-top--medium">
        <Button appearance="base" onClick={() => setSidebar(null)} type="button">
          Cancel
        </Button>
        {/* TODO: Activate the "delete" button when API is ready https://warthogs.atlassian.net/browse/MAASENG-4439 */}
        <ActionButton appearance="negative" onClick={() => {}} type="submit">
          Remove image source
        </ActionButton>
      </div>
    </div>
  );
};

export default DeleteImageSource;
