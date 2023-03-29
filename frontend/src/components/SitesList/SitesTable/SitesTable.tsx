import { useEffect, useMemo } from "react";

import { useReactTable, flexRender, getCoreRowModel } from "@tanstack/react-table";
import type { ColumnDef, Column, Getter, Row } from "@tanstack/react-table";
import pick from "lodash/fp/pick";
import useLocalStorageState from "use-local-storage-state";

import ConnectionInfo from "./ConnectionInfo/ConnectionInfo";
import SitesTableControls from "./SitesTableControls/SitesTableControls";

import type { SitesQueryResult } from "@/api/types";
import { isDev } from "@/constants";
import { useAppContext } from "@/context";
import type { UseSitesQueryResult } from "@/hooks/api";
import { getCountryName, getTimeByUTCOffset, getTimezoneUTCString } from "@/utils";

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
  setSearchText,
}: Pick<UseSitesQueryResult, "data" | "isLoading" | "isFetchedAfterMount"> & {
  setSearchText: (text: string) => void;
}) => {
  const [columnVisibility, setColumnVisibility] = useLocalStorageState("sitesTableColumnVisibility", {
    defaultValue: {},
  });

  const { rowSelection, setRowSelection } = useAppContext();

  // clear selection on unmount
  useEffect(() => {
    return () => setRowSelection({});
  }, [setRowSelection]);

  const columns = useMemo<SitesColumnDef[]>(
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
        cell: ({ row, getValue }: { row: Row<Site>; getValue: Getter<Site["name"]> }) => {
          return (
            <label className="p-checkbox--inline">
              <input
                aria-label={getValue()}
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
            <div className="connection__text">connection</div>
            <div className="connection__text u-text--muted">last seen</div>
          </>
        ),
        cell: ({ getValue }) => {
          const { connection, last_seen } = getValue();
          return connection ? <ConnectionInfo connection={connection} lastSeen={last_seen} /> : null;
        },
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
              <div>{countrycode ? getCountryName(countrycode) : ""}</div>
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
            <div>local time (24hr)</div>
          </>
        ),
        cell: ({ getValue }) => {
          const { timezone } = getValue();
          return Number.isInteger(timezone) ? (
            <>
              <div>
                {getTimeByUTCOffset(new Date(), timezone!)} UTC{getTimezoneUTCString(timezone!)}
              </div>
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

  // wrap the empty array in useMemo to avoid re-rendering the empty table on every render
  const noItems = useMemo<Site[]>(() => [], []);
  const pageCount = data && "total" in data ? Math.ceil(data.total / data.size) : 0;
  const pageIndex = data && "page" in data ? data.page : 0;
  const pageSize = data && "size" in data ? data.size : 0;
  const table = useReactTable<Site>({
    data: data?.items || noItems,
    columns,
    state: {
      rowSelection,
      columnVisibility,
      pagination: {
        pageIndex,
        pageSize,
      },
    },
    getRowId: (row) => row.identifier,
    manualPagination: true,
    pageCount,
    onColumnVisibilityChange: setColumnVisibility,
    enableRowSelection: true,
    enableMultiRowSelection: true,
    onRowSelectionChange: setRowSelection,
    enableColumnResizing: false,
    columnResizeMode: "onChange",
    getCoreRowModel: getCoreRowModel(),
    debugTable: isDev,
    debugHeaders: isDev,
    debugColumns: isDev,
  });

  return (
    <>
      <SitesTableControls
        allColumns={table.getAllLeafColumns()}
        data={data}
        isLoading={isLoading}
        setSearchText={setSearchText}
      />
      <table aria-label="sites" className="sites-table">
        <thead>
          {table.getHeaderGroups().map((headerGroup) => (
            <tr key={headerGroup.id}>
              {headerGroup.headers.map((header) => {
                return (
                  <th className={`${header.column.id}`} colSpan={header.colSpan} key={header.id}>
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

export default SitesTable;
