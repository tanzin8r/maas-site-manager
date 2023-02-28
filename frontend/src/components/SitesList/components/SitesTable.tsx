import {
  useReactTable,
  flexRender,
  ColumnDef,
  getCoreRowModel,
  getFilteredRowModel,
  getPaginationRowModel,
} from "@tanstack/react-table";
import { Input } from "@canonical/react-components";
import { useMemo, useState } from "react";
import pick from "lodash/fp/pick";
import { format } from "date-fns";
import { utcToZonedTime } from "date-fns-tz";
import { Site } from "../../../api/types";

const createAccessor =
  <T, K extends keyof T>(keys: K[] | K) =>
  (row: T) =>
    pick(keys, row);

const SitesTable = ({ data }: { data: Site[] }) => {
  const [columnVisibility, setColumnVisibility] = useState({});

  const columns = useMemo<ColumnDef<Site, Partial<Site>>[]>(
    () => [
      {
        id: "select",
        header: ({ table }) => (
          <div>
            <Input
              type="checkbox"
              {...{
                checked: table.getIsAllRowsSelected(),
                indeterminate: table.getIsSomeRowsSelected(),
                onChange: table.getToggleAllRowsSelectedHandler(),
              }}
            />
          </div>
        ),
        cell: ({ row }) => (
          <div>
            <Input
              type="checkbox"
              {...{
                checked: row.getIsSelected(),
                disabled: !row.getCanSelect(),
                indeterminate: row.getIsSomeSelected(),
                onChange: row.getToggleSelectedHandler(),
              }}
            />
          </div>
        ),
      },
      {
        id: "name",
        accessorFn: createAccessor(["name", "url"]),
        header: () => (
          <>
            <div>Name</div>
            <div className="u-text--muted">URL</div>
          </>
        ),
        cell: ({ getValue }) => (
          <>
            <div>{getValue().name}</div>
            <div className="u-text--muted">{getValue().url}</div>
          </>
        ),
      },
      {
        id: "connection",
        accessorFn: createAccessor(["connection", "last_seen"]),
        header: () => (
          <>
            <div>connection</div>
            <div className="u-text--muted">last seen</div>
          </>
        ),
        cell: ({ getValue }) => (
          <>
            <div>{getValue().connection}</div>
            <div className="u-text--muted">{getValue().last_seen}</div>
          </>
        ),
      },
      {
        id: "address",
        accessorFn: createAccessor("address"),
        header: () => (
          <>
            <div>country</div>
            <div className="u-text--muted">street, city, ZIP</div>
          </>
        ),
        cell: ({ getValue }) => {
          const { address } = getValue();
          const { countrycode, city, zip, street } = address || {};
          return (
            <>
              <div>{countrycode}</div>
              <div className="u-text--muted">
                {street}, {city}, {zip}
              </div>
            </>
          );
        },
      },
      {
        id: "time",
        accessorFn: createAccessor("timezone"),
        header: () => (
          <>
            <div>local time</div>
            <div className="u-text--muted">timezone</div>
          </>
        ),
        cell: ({ getValue }) => {
          const { timezone } = getValue();
          return timezone ? (
            <>
              <div>
                {format(utcToZonedTime(new Date(), timezone), "HH:mm")} (local
                time)
              </div>
              <div className="u-text--muted">{timezone}</div>
            </>
          ) : null;
        },
      },
      {
        id: "status",
        accessorFn: createAccessor("stats"),
        header: () => (
          <>
            <div>machines</div>
            <div className="u-text--muted">aggregated status</div>
          </>
        ),
        cell: ({ getValue }) => {
          const { stats } = getValue();
          const {
            machines,
            ready_machines,
            occupied_machines,
            error_machines,
          } = stats || {};
          return (
            <>
              <div>{machines}</div>
              <div className="u-text--muted">
                Ready: {ready_machines}, Occupied: {occupied_machines}, Error:{" "}
                {error_machines}
              </div>
            </>
          );
        },
      },
    ],
    []
  );

  const [rowSelection, setRowSelection] = useState({});

  const table = useReactTable<Site>({
    data: data || [],
    columns,
    state: {
      rowSelection,
      columnVisibility,
    },
    onColumnVisibilityChange: setColumnVisibility,
    enableRowSelection: true,
    onRowSelectionChange: setRowSelection,
    enableColumnResizing: false,
    columnResizeMode: "onChange",
    getCoreRowModel: getCoreRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    debugTable: true,
    debugHeaders: true,
    debugColumns: true,
  });

  return (
    <table className="u-table-layout--auto" aria-label="sites">
      <thead>
        {table.getHeaderGroups().map((headerGroup) => (
          <tr key={headerGroup.id}>
            {headerGroup.headers.map((header) => {
              return (
                <th key={header.id} colSpan={header.colSpan}>
                  {header.isPlaceholder
                    ? null
                    : flexRender(
                        header.column.columnDef.header,
                        header.getContext()
                      )}
                  {header.column.getCanResize() && (
                    <div
                      onMouseDown={header.getResizeHandler()}
                      onTouchStart={header.getResizeHandler()}
                      className={`resizer ${
                        header.column.getIsResizing() ? "isResizing" : ""
                      }`}
                    ></div>
                  )}
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
                  <td key={cell.id}>
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

export default SitesTable;
