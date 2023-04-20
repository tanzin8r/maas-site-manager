import type { RowData, Table } from "@tanstack/react-table";

import { useAppContext } from "@/context";

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

function SelectAllCheckbox<T>({ table }: Props<T>) {
  // TODO: remove this workaround once the issue below is fixed
  // https://github.com/TanStack/table/issues/4781
  // manually check if some rows are selected as getIsSomePageRowsSelected
  // returns false if there are any rows selected on other pages
  const { rowSelection } = useAppContext();
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
