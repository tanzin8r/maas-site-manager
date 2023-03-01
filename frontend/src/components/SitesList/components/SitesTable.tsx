import { useMemo, useState } from "react";

import { Input } from "@canonical/react-components";
import {
  useReactTable,
  flexRender,
  getCoreRowModel,
  getFilteredRowModel,
  getPaginationRowModel,
} from "@tanstack/react-table";
import type { ColumnDef, Column } from "@tanstack/react-table";
import { format } from "date-fns";
import { utcToZonedTime } from "date-fns-tz";
import pick from "lodash/fp/pick";
import useLocalStorageState from "use-local-storage-state";

import type { SitesQueryResult } from "../../../api/types";
import type { UseSitesQueryResult } from "../../../hooks/api";

import "./SitesTable.scss";
import SitesTableControls from "./SitesTableControls";

const createAccessor =
  <T, K extends keyof T>(keys: K[] | K) =>
  (row: T) =>
    pick(keys, row);

export type Site = SitesQueryResult["items"][number];
export type SitesColumnDef = ColumnDef<Site, Partial<Site>>;
export type SitesColumn = Column<Site, unknown>;

const SitesTable = ({
  data,
  isFetchedAfterMount,
  isLoading,
}: Pick<UseSitesQueryResult, "data" | "isLoading" | "isFetchedAfterMount">) => {
  const [columnVisibility, setColumnVisibility] = useLocalStorageState("sitesTableColumnVisibility", {
    defaultValue: {},
  });

  const columns = useMemo<SitesColumnDef[]>(
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
              <div>{format(utcToZonedTime(new Date(), timezone), "HH:mm")} (local time)</div>
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
          const { machines, ready_machines, occupied_machines, error_machines } = stats || {};
          return (
            <>
              <div>{machines}</div>
              <div className="u-text--muted">
                Ready: {ready_machines}, Occupied: {occupied_machines}, Error: {error_machines}
              </div>
            </>
          );
        },
      },
    ],
    [],
  );

  const [rowSelection, setRowSelection] = useState({});

  const table = useReactTable<Site>({
    data: data?.items || [],
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
    <>
      <SitesTableControls allColumns={table.getAllLeafColumns()} data={data} isLoading={isLoading} />
      <table aria-label="sites" className="sites-table">
        <thead>
          {table.getHeaderGroups().map((headerGroup) => (
            <tr key={headerGroup.id}>
              {headerGroup.headers.map((header) => {
                return (
                  <th colSpan={header.colSpan} key={header.id}>
                    {header.isPlaceholder ? null : flexRender(header.column.columnDef.header, header.getContext())}
                    {header.column.getCanResize() && (
                      <div
                        className={`resizer ${header.column.getIsResizing() ? "isResizing" : ""}`}
                        onMouseDown={header.getResizeHandler()}
                        onTouchStart={header.getResizeHandler()}
                      ></div>
                    )}
                  </th>
                );
              })}
            </tr>
          ))}
        </thead>
        {isLoading && !isFetchedAfterMount ? (
          <caption>Loading...</caption>
        ) : (
          <tbody>
            {table.getRowModel().rows.map((row) => {
              return (
                <tr key={row.id}>
                  {row.getVisibleCells().map((cell) => {
                    return <td key={cell.id}>{flexRender(cell.column.columnDef.cell, cell.getContext())}</td>;
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

export default SitesTable;
