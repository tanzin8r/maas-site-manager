import type { ColumnDef } from "@tanstack/react-table";
import { useReactTable, flexRender, getCoreRowModel } from "@tanstack/react-table";

import SelectAllCheckbox from "./SelectAllCheckbox";

import { render, screen } from "@/test-utils";

type ColDef = ColumnDef<unknown, unknown>;

const columns: ColDef[] = [
  {
    id: "select",
    header: ({ table }) => <SelectAllCheckbox table={table} />,
    cell: ({ row }) => {
      return (
        <input
          className="p-checkbox__input"
          type="checkbox"
          {...{
            checked: row.getIsSelected(),
            disabled: !row.getCanSelect(),
            onChange: row.getToggleSelectedHandler(),
          }}
        />
      );
    },
  },
];

const SelectAllCheckboxWithTable = () => {
  const table = useReactTable<unknown>({
    data: Array.from({ length: 100 }, (_, i) => i + 1),
    columns,
    getCoreRowModel: getCoreRowModel(),
  });
  return (
    <table aria-label="sites" className="sites-table">
      <thead>
        {table.getHeaderGroups().map((headerGroup) => (
          <tr key={headerGroup.id}>
            {headerGroup.headers.map((header) => {
              return (
                <th className={`${header.column.id}`} colSpan={header.colSpan} key={header.id}>
                  {flexRender(header.column.columnDef.header, header.getContext())}
                </th>
              );
            })}
          </tr>
        ))}
      </thead>
      <tbody>
        {table.getRowModel().rows.map((row) => {
          return (
            <tr key={row.id}>
              {row.getVisibleCells().map((cell) => {
                return (
                  <td className={`${cell.column.id}`} key={cell.id}>
                    {flexRender(cell.column.columnDef.cell, cell.getContext())}
                  </td>
                );
              })}
            </tr>
          );
        })}
      </tbody>
    </table>
  );
};

it("toggles select all checkbox on click", async () => {
  render(<SelectAllCheckboxWithTable />);
  await expect(screen.getByRole("checkbox", { name: /select all/i })).not.toBeChecked();
  await screen.getByRole("checkbox", { name: /select all/i }).click();
  await expect(screen.getByRole("checkbox", { name: /select all/i })).toBeChecked();
});
