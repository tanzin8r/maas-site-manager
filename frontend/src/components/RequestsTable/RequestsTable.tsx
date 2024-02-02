import { useMemo } from "react";

import { ExternalLink } from "@canonical/maas-react-components";
import { useReactTable, flexRender, getCoreRowModel } from "@tanstack/react-table";
import type { Column, ColumnDef } from "@tanstack/react-table";

import type { PendingSite } from "@/api-client/models/PendingSite";
import DateTime from "@/components/DateTime";
import DynamicTable from "@/components/DynamicTable/DynamicTable";
import SelectAllCheckbox from "@/components/SelectAllCheckbox";
import TableCaption from "@/components/TableCaption";
import docsUrls from "@/config/docsUrls";
import { isDev } from "@/constants";
import { useRowSelection } from "@/context/RowSelectionContext/RowSelectionContext";
import type { UseEnrollmentRequestsQueryResult } from "@/hooks/react-query";

export type EnrollmentRequestsColumnDef = ColumnDef<PendingSite, PendingSite[keyof PendingSite]>;
export type EnrollmentRequestsColumn = Column<PendingSite, unknown>;

const RequestsTable = ({
  data,
  error,
  isPending,
}: Pick<UseEnrollmentRequestsQueryResult, "data" | "error" | "isPending">) => {
  const { rowSelection, setRowSelection } = useRowSelection("requests", { clearOnUnmount: true });

  const columns = useMemo<EnrollmentRequestsColumnDef[]>(
    () => [
      {
        id: "select",
        accessorKey: "name",
        header: ({ table }) => <SelectAllCheckbox table={table} tableId="requests" />,
        cell: ({ row, getValue }) => {
          return (
            <label className="p-checkbox--inline">
              <input
                aria-label={`select ${getValue()}`}
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
        header: () => <div>Name</div>,
      },
      {
        id: "url",
        accessorKey: "url",
        header: () => <div>URL</div>,
        cell: ({ getValue }) => <ExternalLink to={String(getValue())}>{getValue()}</ExternalLink>,
      },
      {
        id: "created",
        accessorKey: "created",
        header: () => <div>Time of request (UTC)</div>,
        cell: ({ getValue }) => <DateTime value={String(getValue())} />,
      },
    ],
    [],
  );

  // wrap the empty array in useMemo to avoid re-rendering the empty table on every render
  const noItems = useMemo<PendingSite[]>(() => [], []);
  const table = useReactTable<PendingSite>({
    data: data?.items || noItems,
    columns,
    state: {
      rowSelection,
    },
    getRowId: (row) => `${row.id}`,
    manualPagination: true,
    enableRowSelection: true,
    enableMultiRowSelection: true,
    onRowSelectionChange: setRowSelection,
    getCoreRowModel: getCoreRowModel(),
    debugTable: isDev,
    debugHeaders: isDev,
    debugColumns: isDev,
  });

  return (
    <DynamicTable aria-label="enrollment requests" className="sites-table">
      <thead>
        {table.getHeaderGroups().map((headerGroup) => (
          <tr key={headerGroup.id}>
            {headerGroup.headers.map((header) => {
              return (
                <th className={`${header.column.id}`} colSpan={header.colSpan} key={header.id}>
                  {header.isPlaceholder ? null : flexRender(header.column.columnDef.header, header.getContext())}
                </th>
              );
            })}
          </tr>
        ))}
      </thead>
      {error ? (
        <TableCaption>
          <TableCaption.Error error={error} />
        </TableCaption>
      ) : isPending ? (
        <DynamicTable.Loading table={table} />
      ) : table.getRowModel().rows.length < 1 ? (
        <TableCaption>
          <TableCaption.Title>No outstanding requests</TableCaption.Title>
          <TableCaption.Description>
            You have to request an enrolment in the site-manager-agent.
            <br />
            <ExternalLink to={docsUrls.enrollmentRequest}>Read more about it in the documentation.</ExternalLink>
          </TableCaption.Description>
        </TableCaption>
      ) : (
        <DynamicTable.Body>
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
        </DynamicTable.Body>
      )}
    </DynamicTable>
  );
};

export default RequestsTable;
