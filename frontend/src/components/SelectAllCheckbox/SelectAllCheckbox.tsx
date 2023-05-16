import type { RowData, Table } from "@tanstack/react-table";

import type { TableId } from "@/context/RowSelectionContext";
import { useRowSelectionContext } from "@/context/RowSelectionContext";

type Props<T> = {
  table: Table<T>;
};

// TODO: replace with table.getToggleAllPageRowsSelectedHandler once the issue below is fixed
// https://github.com/TanStack/table/issues/4781
const selectAllPageRows = <T extends RowData>(table: Table<T>) =>
  table.setRowSelection((previousSelection) => {
    return {
      ...previousSelection,
      ...Object.keys(table.getRowModel().rowsById).reduce((acc, id) => ({ ...acc, [id]: true }), {}),
    };
  });

function SelectAllCheckbox<T>({ table, tableId }: Props<T> & { tableId: TableId }) {
  // TODO: remove this workaround once the issue below is fixed
  // https://github.com/TanStack/table/issues/4781
  // manually check if some rows are selected as getIsSomePageRowsSelected
  // returns false if there are any rows selected on other pages
  const { rowSelection } = useRowSelectionContext(tableId);
  const isSomeRowsSelected = !table.getIsAllPageRowsSelected() && Object.keys(rowSelection).length > 0;
  return (
    <label className="p-checkbox--inline">
      <input
        aria-checked={isSomeRowsSelected ? "mixed" : undefined}
        aria-label="select all"
        className="p-checkbox__input"
        type="checkbox"
        {...{
          checked: isSomeRowsSelected || table.getIsAllPageRowsSelected(),
          onChange: () => {
            if (table.getIsAllPageRowsSelected()) {
              table.resetRowSelection();
            } else {
              selectAllPageRows<T>(table);
            }
          },
        }}
      />
      <span className="p-checkbox__label" />
    </label>
  );
}

export default SelectAllCheckbox;
