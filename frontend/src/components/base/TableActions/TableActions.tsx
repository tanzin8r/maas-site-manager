import { Button, Tooltip } from "@canonical/react-components";
import classNames from "classnames";

import type { To } from "@/utils/router";
import { Link } from "@/utils/router";

type Props = {
  className?: string;
  hasBorder?: boolean;
  onEdit?: () => void;
  onDelete?: () => void;
  editTooltip?: string;
  deleteTooltip?: string;
  editDisabled?: boolean;
  deleteDisabled?: boolean;
  editPath?: To;
};

const TableActions = ({
  className,
  hasBorder,
  editTooltip,
  deleteTooltip,
  onEdit,
  onDelete,
  editDisabled,
  editPath,
  deleteDisabled,
}: Props) => {
  return (
    <div className={classNames("table-actions u-flex", { "table-actions-bordered": hasBorder }, className)}>
      {onEdit && (
        <Tooltip message={editTooltip} position="left">
          <Button
            appearance="base"
            className="is-dense u-table-cell-padding-overlap table-actions-btn"
            disabled={editDisabled}
            element={editPath ? Link : undefined}
            hasIcon
            onClick={() => (onEdit ? onEdit() : null)}
            to={editPath ? editPath : undefined}
          >
            <i className="p-icon--edit">Edit</i>
          </Button>
        </Tooltip>
      )}
      <span className="table-actions-vertical-divider"></span>
      {onDelete && (
        <Tooltip message={deleteTooltip} position="left">
          <Button
            appearance="base"
            className="is-dense u-table-cell-padding-overlap table-actions-btn"
            disabled={deleteDisabled}
            hasIcon
            onClick={() => onDelete()}
            type="button"
          >
            <i className="p-icon--delete">Delete</i>
          </Button>
        </Tooltip>
      )}
    </div>
  );
};

export default TableActions;
