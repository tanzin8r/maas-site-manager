import { Button, Notification } from "@canonical/react-components";

import EnrollmentNotification from "./EnrollmentNotification";

import { useRowSelectionContext } from "@/context/RowSelectionContext";
import { useEnrollmentRequestsMutation } from "@/hooks/react-query";

const EnrollmentActions: React.FC = () => {
  const { rowSelection, setRowSelection } = useRowSelectionContext("requests");
  const selectedIds = Object.keys(rowSelection).map((id) => id);
  const enrollmentRequestsMutation = useEnrollmentRequestsMutation({ onSuccess: () => setRowSelection({}) });
  const isActionDisabled = Object.keys(rowSelection).length === 0 || enrollmentRequestsMutation.isLoading;
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
      <div className="u-fixed-width">
        {enrollmentRequestsMutation.isSuccess ? (
          <EnrollmentNotification {...enrollmentRequestsMutation.variables} />
        ) : null}
        {enrollmentRequestsMutation.isError ? (
          <Notification role="alert" severity="negative">
            There was an error processing enrolment request(s).
          </Notification>
        ) : null}
        <div className="u-flex u-flex--justify-end">
          <Button appearance="negative" disabled={isActionDisabled} onClick={handleDeny} type="button">
            Deny
          </Button>
          <Button appearance="positive" disabled={isActionDisabled} onClick={handleAccept} type="button">
            Accept
          </Button>
        </div>
      </div>
    </>
  );
};

export default EnrollmentActions;
