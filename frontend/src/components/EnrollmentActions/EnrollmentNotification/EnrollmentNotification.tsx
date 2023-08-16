import { Notification } from "@canonical/react-components";
import pluralize from "pluralize";

import type { PendingSitesPostRequest } from "@/api-client/models/PendingSitesPostRequest";
import { useNavigate } from "@/utils/router";

const EnrollmentNotification = ({ accept, ids }: Partial<PendingSitesPostRequest>) => {
  const navigate = useNavigate();
  return (
    <Notification
      actions={[{ label: "Go to Sites", onClick: () => navigate("/sites") }]}
      role="alert"
      severity="information"
      title={accept ? "Accepted" : "Denied"}
    >
      {accept ? "Accepted" : "Denied"} enrolment request for {pluralize("MAAS sites", ids?.length, true)}. See more data
      of this site in the Sites page.
    </Notification>
  );
};

export default EnrollmentNotification;
