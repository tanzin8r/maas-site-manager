import type { Row } from "@tanstack/react-table";

import type { Image } from "@/mocks/factories";

type SelectGroupCheckboxProps = { row: Row<Image> };

const SelectGroupCheckbox: React.FC<SelectGroupCheckboxProps> = ({ row }) => {
  return (
    <label className="p-checkbox--inline">
      <input
        aria-checked={row.getIsSomeSelected() ? "mixed" : undefined}
        aria-label={row.original?.name}
        className="p-checkbox__input"
        type="checkbox"
        {...{
          checked: row.getIsSelected() || row.getIsAllSubRowsSelected(),
          disabled: !row.getCanSelect(),
          onChange: () => {
            if (row.getIsSelected() || row.getIsSomeSelected()) {
              row.toggleSelected(false);
              row.subRows.forEach((subRow) => subRow.toggleSelected(false));
            } else {
              row.toggleSelected(true);
              row.subRows.forEach((subRow) => subRow.toggleSelected(true));
            }
          },
        }}
      />
      <span className="p-checkbox__label" />
    </label>
  );
};

export default SelectGroupCheckbox;
