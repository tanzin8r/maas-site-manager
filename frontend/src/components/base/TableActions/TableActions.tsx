import { Button, Tooltip } from "@canonical/react-components";
import classNames from "classnames";

type Props = {
  className?: string;
  hasBorder?: boolean;
  onEdit?: () => void;
  onDelete?: () => void;
  onExpand?: () => void;
  editTooltip?: string;
  deleteTooltip?: string;
  editDisabled?: boolean;
  deleteDisabled?: boolean;
};

const TableActions = ({
  className,
  hasBorder,
  editTooltip,
  deleteTooltip,
  onEdit,
  onDelete,
  onExpand,
  editDisabled,
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
            hasIcon
            onClick={onEdit}
            type="button"
          >
            <i className="p-icon--edit">Edit</i>
          </Button>
        </Tooltip>
      )}
      {onExpand ? (
        <Button appearance="base" onClick={onExpand} type="button">
          expand
        </Button>
      ) : (
        <>
          {onEdit && onDelete ? <span className="table-actions-vertical-divider"></span> : null}
          {onDelete && (
            <Tooltip message={deleteTooltip} position="left">
              <Button
                appearance="base"
                className="is-dense u-table-cell-padding-overlap table-actions-btn"
                disabled={deleteDisabled}
                hasIcon
                onClick={onDelete}
                type="button"
              >
                <i className="p-icon--delete">Delete</i>
              </Button>
            </Tooltip>
          )}
        </>
      )}
    </div>
  );
};

export default TableActions;
