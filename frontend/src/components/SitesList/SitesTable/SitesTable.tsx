import { useEffect, useMemo } from "react";

import { useReactTable, flexRender, getCoreRowModel } from "@tanstack/react-table";
import type { ColumnDef, Column, Getter, Row } from "@tanstack/react-table";
import classNames from "classnames";
import pick from "lodash/fp/pick";
import useLocalStorageState from "use-local-storage-state";

import AggregatedStats from "./AggregatedStatus";
import ConnectionInfo from "./ConnectionInfo";
import SitesTableControls from "./SitesTableControls/SitesTableControls";

import type { SitesQueryResult } from "@/api/types";
import ExternalLink from "@/components/ExternalLink";
import NoRegions from "@/components/NoRegions";
import SelectAllCheckbox from "@/components/SelectAllCheckbox";
import { isDev } from "@/constants";
import { useAppContext } from "@/context";
import type { UseSitesQueryResult } from "@/hooks/api";
import { getAllMachines, getCountryName, getTimezoneUTCString, getTimeInTimezone } from "@/utils";

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
        header: ({ table }) => <SelectAllCheckbox table={table} />,
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
            <ExternalLink to={getValue().url || ""}>{getValue().url}</ExternalLink>
          </>
        ),
      },
      {
        id: "connection",
        accessorFn: createAccessor("stats"),
        header: () => (
          <>
            <div className="connection__text">connection</div>
            <div className="connection__text u-text--muted">last seen</div>
          </>
        ),
        cell: ({ getValue }) => {
          const { stats } = getValue();
          return stats ? <ConnectionInfo connection={stats.connection} lastSeen={stats.last_seen} /> : null;
        },
      },
      {
        id: "address",
        accessorFn: createAccessor(["country", "city", "zip", "street"]),
        header: () => (
          <>
            <div>country</div>
            <div className="u-text--muted">street, city, ZIP</div>
          </>
        ),
        cell: ({ getValue }) => {
          const { country, city, zip, street } = getValue();
          return (
            <>
              <div>{country ? getCountryName(country) : ""}</div>
              <div className="u-text--muted">
                {street}, {city}, {zip}
              </div>
            </>
          );
        },
      },
      {
        id: "time",
        accessorFn: createAccessor(["timezone"]),
        header: () => (
          <>
            <div>local time (24hr)</div>
          </>
        ),
        cell: ({ getValue }) => {
          const { timezone } = getValue();
          return timezone ? (
            <div>
              {getTimeInTimezone(new Date(), timezone)} UTC{getTimezoneUTCString(timezone)}
            </div>
          ) : null;
        },
      },
      {
        id: "machines",
        accessorFn: createAccessor("stats"),
        header: () => (
          <>
            <div>machines</div>
          </>
        ),
        cell: ({ getValue }) => {
          const { stats } = getValue();
          return stats ? getAllMachines(stats) : null;
        },
      },
      {
        id: "status",
        accessorFn: createAccessor("stats"),
        header: () => (
          <>
            <div>aggregated status</div>
          </>
        ),
        cell: ({ getValue }) => {
          const { stats } = getValue();
          return stats ? <AggregatedStats stats={stats} /> : null;
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
    getRowId: (row) => row.id,
    manualPagination: true,
    pageCount,
    onColumnVisibilityChange: setColumnVisibility,
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
                  </th>
                );
              })}
            </tr>
          ))}
        </thead>
        {isLoading && !isFetchedAfterMount ? (
          <caption>Loading...</caption>
        ) : table.getRowModel().rows.length < 1 ? (
          <NoRegions />
        ) : (
          <tbody>
            {table.getRowModel().rows.map((row) => {
              return (
                <tr
                  className={classNames({ "sites-table-row--muted": row.original.stats?.connection === "unknown" })}
                  key={row.id}
                >
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
