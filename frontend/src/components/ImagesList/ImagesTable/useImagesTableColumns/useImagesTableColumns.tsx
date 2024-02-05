import { useMemo } from "react";

import { formatBytes } from "@canonical/maas-react-components";
import { Icon } from "@canonical/react-components";
import type { ColumnDef, Row, Getter, Table } from "@tanstack/react-table";
import pluralize from "pluralize";

import type { Image } from "@/api";
import SyncStatus from "@/components/ImagesList/ImagesTable/SyncStatus";
import SelectAllCheckbox from "@/components/SelectAllCheckbox";
import SelectGroupCheckbox from "@/components/SelectGroupCheckbox/SelectGroupCheckbox";
import GroupRowActions from "@/components/base/GroupRowActions";
import TableActions from "@/components/base/TableActions";
import { useAppLayoutContext } from "@/context";
export type ImageColumnDef = ColumnDef<Image, Partial<Image>>;

const useImagesTableColumns = () => {
  const { setSidebar } = useAppLayoutContext();

  return useMemo<ImageColumnDef[]>(
    () => [
      {
        id: "select",
        accessorKey: "id",
        enableSorting: false,
        header: ({ table }) => <SelectAllCheckbox table={table} tableId="images" />,
        cell: ({ row }: { row: Row<Image> }) => {
          return row.getIsGrouped() ? (
            <SelectGroupCheckbox row={row} />
          ) : (
            <label className="p-checkbox--inline">
              <input
                aria-label={row.original.name}
                className="p-checkbox__input"
                type="checkbox"
                {...{
                  checked: row.getIsSelected(),
                  disabled: !row.getCanSelect(),
                  onChange: row.getToggleSelectedHandler(),
                }}
              />
              <span className="p-checkbox__label" />
            </label>
          );
        },
      },
      {
        id: "name",
        accessorKey: "name",
        cell: ({ row, getValue }: { row: Row<Image>; getValue: Getter<Image["name"]> }) => {
          return (
            <div>
              <div>
                <strong>{getValue()}</strong>
              </div>
              <small className="u-text--muted">{pluralize("image", row.getLeafRows().length ?? 0, true)}</small>
            </div>
          );
        },
      },
      { id: "release", accessorKey: "release", enableSorting: true, header: () => "Release title" },
      {
        id: "architecture",
        accessorKey: "architecture",
        enableSorting: false,
        header: () => "Architecture",
      },
      {
        id: "size",
        accessorKey: "size",
        enableSorting: false,
        header: () => "Size",
        cell: ({ getValue }: { getValue: Getter<Image["size"]> }) => {
          const { value, unit } = formatBytes({ value: getValue(), unit: "B" });
          return `${value} ${unit}`;
        },
      },
      {
        id: "status",
        accessorKey: "status",
        enableSorting: false,
        header: () => "Status",
        cell: ({ row }) => <SyncStatus image={row.original} />,
      },
      {
        id: "custom",
        accessorKey: "is_custom_image",
        enableSorting: false,
        header: "Custom",
        cell: ({ getValue }: { getValue: Getter<Image["is_custom_image"]> }) =>
          getValue() ? <Icon aria-label="checked" name="task-outstanding" role="img" /> : null,
      },
      {
        id: "action",
        accessorKey: "id",
        header: () => "Action",
        enableSorting: false,
        cell: ({ row, getValue }: { table: Table<Image>; row: Row<Image>; getValue: Getter<Image["id"]> }) => {
          const id = getValue();
          return row.getIsGrouped() ? (
            <GroupRowActions getIsExpanded={row.getIsExpanded} toggleExpanded={row.toggleExpanded} />
          ) : (
            <TableActions
              className="u-align--right"
              deleteDisabled={row.getIsGrouped() ? !row.getCanSelectSubRows() : !row.getCanSelect()}
              hasBorder
              onDelete={() => {
                if (id) {
                  if (!row.getIsSelected()) {
                    row.toggleSelected();
                  }
                  setSidebar("deleteImages");
                }
              }}
            />
          );
        },
      },
    ],
    [setSidebar],
  );
};
export default useImagesTableColumns;
