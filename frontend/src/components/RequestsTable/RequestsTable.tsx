import { useEffect, useMemo } from "react";

import { useReactTable, flexRender, getCoreRowModel, createColumnHelper } from "@tanstack/react-table";
import type { Column, Getter, Row, ColumnDef } from "@tanstack/react-table";

import type { EnrollmentRequest } from "@/api/types";
import docsUrls from "@/base/docsUrls";
import DateTime from "@/components/DateTime";
import ExternalLink from "@/components/ExternalLink";
import TableCaption from "@/components/TableCaption";
import { isDev } from "@/constants";
import { useAppContext } from "@/context";
import type { UseEnrollmentRequestsQueryResult } from "@/hooks/api";

export type EnrollmentRequestsColumnDef = ColumnDef<EnrollmentRequest, EnrollmentRequest[keyof EnrollmentRequest]>;
export type EnrollmentRequestsColumn = Column<EnrollmentRequest, unknown>;

const columnHelper = createColumnHelper<EnrollmentRequest>();

const RequestsTable = ({
  data,
  isFetchedAfterMount,
  isLoading,
}: Pick<UseEnrollmentRequestsQueryResult, "data" | "isLoading" | "isFetchedAfterMount">) => {
  const { rowSelection, setRowSelection } = useAppContext();

  // clear selection on unmount
  useEffect(() => {
    return () => setRowSelection({});
  }, [setRowSelection]);

  const columns = useMemo<EnrollmentRequestsColumnDef[]>(
    () => [
      {
        id: "select",
        accessorKey: "name",
        header: ({ table }) => (
          <label className="p-checkbox--inline">
            <input
              aria-checked={table.getIsSomeRowsSelected() || table.getIsSomePageRowsSelected() ? "mixed" : undefined}
              aria-label="select all"
              className="p-checkbox__input"
              type="checkbox"
              {...{
                checked:
                  table.getIsSomePageRowsSelected() ||
                  table.getIsSomeRowsSelected() ||
                  table.getIsAllPageRowsSelected(),
                onChange: table.getToggleAllPageRowsSelectedHandler(),
              }}
            />
            <span className="p-checkbox__label" />
          </label>
        ),
        cell: ({ row, getValue }: { row: Row<EnrollmentRequest>; getValue: Getter<EnrollmentRequest["name"]> }) => {
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
      columnHelper.accessor("name", {
        id: "name",
        header: () => <div>Name</div>,
      }),
      columnHelper.accessor("url", {
        id: "url",
        header: () => <div>URL</div>,
        cell: ({ getValue }) => <ExternalLink to={getValue()}>{getValue()}</ExternalLink>,
      }),
      columnHelper.accessor("created", {
        id: "created",
        header: () => <div>Time of request (UTC)</div>,
        cell: ({ getValue }) => <DateTime value={getValue()} />,
      }),
    ],
    [],
  );

  // wrap the empty array in useMemo to avoid re-rendering the empty table on every render
  const noItems = useMemo<EnrollmentRequest[]>(() => [], []);
  const table = useReactTable<EnrollmentRequest>({
    data: data?.items || noItems,
    columns,
    state: {
      rowSelection,
    },
    getRowId: (row) => row.id,
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
    <>
      <table aria-label="enrollment requests" className="sites-table">
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
        {isLoading && !isFetchedAfterMount ? (
          <caption>Loading...</caption>
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
        )}
      </table>
    </>
  );
};

export default RequestsTable;
