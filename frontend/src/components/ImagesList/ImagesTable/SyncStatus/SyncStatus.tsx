import { Icon } from "@canonical/react-components";

import type { Image } from "@/api";
import Placeholder from "@/components/Placeholder";
import { useSitesQuery } from "@/hooks/react-query";
import { formatUTCDateString } from "@/utils";

const SyncedStatus = ({ image }: { image: Image }) => {
  return (
    <div>
      <Icon aria-hidden="true" name="success" /> Synced to MAAS sites
      <div>
        <small className="u-text--muted">{image.last_synced ? formatUTCDateString(image.last_synced) : ""}</small>
      </div>
    </div>
  );
};

const SyncingStatus = ({ image, totalSites }: { image: Image; totalSites: number | null }) => (
  <div>
    <Icon aria-hidden="true" className="u-animation--spin" name="spinner" /> Syncing to MAAS sites
    <div>
      <small className="u-text--muted">
        <Placeholder isPending={totalSites === null}>{`${image.number_of_sites_synced} / ${
          totalSites ?? "unknown"
        }`}</Placeholder>
      </small>
    </div>
  </div>
);

const QueuedStatus = () => (
  <div>
    <Icon aria-hidden="true" name="spinner" /> Queued for download
  </div>
);

const DownloadingStatus = ({ image }: { image: Image }) => (
  <div>
    <Icon aria-hidden="true" className="u-animation--spin" name="spinner" /> Downloading {image.downloaded}%
  </div>
);

const syncStatusComponents = {
  synced: SyncedStatus,
  syncing: SyncingStatus,
  queued: QueuedStatus,
  downloading: DownloadingStatus,
};

type Status = keyof typeof syncStatusComponents;
type SyncStatusProps = { status: Status; image: Image; totalSites: number | null };
const SyncStatus = ({ status, image, totalSites }: SyncStatusProps) => {
  const StatusComponent = syncStatusComponents[status];
  return StatusComponent ? <StatusComponent image={image} totalSites={totalSites} /> : null;
};

const getImageStatus = (image: Image, totalSites: number | null): Status | null => {
  if (image.downloaded === 0) {
    return "queued";
  } else if (image.downloaded < 100 && image.number_of_sites_synced === 0) {
    return "downloading";
  } else if (image.number_of_sites_synced === totalSites) {
    return "synced";
  } else if (image.number_of_sites_synced > 0) {
    return "syncing";
  }
  return null;
};

const SyncStatusContainer = ({ image }: { image: Image }) => {
  const totalSites = useSitesQuery({ page: 1, size: 0 }).data?.total ?? null;
  const status = getImageStatus(image, totalSites);
  return status ? <SyncStatus image={image} status={status} totalSites={totalSites} /> : <Placeholder isPending />;
};

export default SyncStatusContainer;
