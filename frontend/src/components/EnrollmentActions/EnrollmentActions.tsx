import { MainToolbar } from "@canonical/maas-react-components";
import { Button, Notification } from "@canonical/react-components";

import EnrollmentNotification from "./EnrollmentNotification";

import RemoveButton from "@/components/base/RemoveButton";
import { useRowSelectionContext } from "@/context/RowSelectionContext";
import { useEnrollmentRequestsMutation } from "@/hooks/react-query";

const EnrollmentActions: React.FC = () => {
  const { rowSelection, setRowSelection } = useRowSelectionContext("requests");
  const selectedIds = Object.keys(rowSelection).map((id) => Number(id));
  const enrollmentRequestsMutation = useEnrollmentRequestsMutation({ onSuccess: () => setRowSelection({}) });
  const isActionDisabled = Object.keys(rowSelection).length === 0 || enrollmentRequestsMutation.isPending;
  const handleAccept = () =>
    enrollmentRequestsMutation.mutate({
      accept: true,
      ids: selectedIds,
    });
  const handleDeny = () =>
    enrollmentRequestsMutation.mutate({
      accept: false,
      ids: selectedIds,
    });

  return (
    <>
      <div className="u-fixed-width enrollment-actions">
        {enrollmentRequestsMutation.isSuccess ? (
          <EnrollmentNotification {...enrollmentRequestsMutation.variables} />
        ) : null}
        {enrollmentRequestsMutation.isError ? (
          <Notification role="alert" severity="negative">
            There was an error processing enrolment request(s).
          </Notification>
        ) : null}
        <MainToolbar>
          <MainToolbar.Title>Enrollment requests</MainToolbar.Title>
          <MainToolbar.Controls>
            <RemoveButton disabled={isActionDisabled} label="Deny" onClick={handleDeny} type="button" />
            <Button appearance="positive" disabled={isActionDisabled} onClick={handleAccept} type="button">
              Accept
            </Button>
          </MainToolbar.Controls>
        </MainToolbar>
      </div>
    </>
  );
};

export default EnrollmentActions;
