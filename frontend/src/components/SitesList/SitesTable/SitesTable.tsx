import type { Dispatch, SetStateAction } from "react";
import React, { useEffect, useMemo } from "react";

import { useReactTable, flexRender, getCoreRowModel } from "@tanstack/react-table";
import type { ColumnDef, Column, Getter, Row, SortingState } from "@tanstack/react-table";
import classNames from "classnames";
import pick from "lodash/fp/pick";
import useLocalStorageState from "use-local-storage-state";

import AggregatedStats from "./AggregatedStatus";
import ConnectionInfo from "./ConnectionInfo";
import ColumnsVisibilityControl from "./SitesTableControls/ColumnsVisibilityControl";
import SitesTableControls from "./SitesTableControls/SitesTableControls";

import type { SitesQueryResult } from "@/api/types";
import DynamicTable from "@/components/DynamicTable/DynamicTable";
import ExternalLink from "@/components/ExternalLink";
import NoRegions from "@/components/NoRegions";
import SelectAllCheckbox from "@/components/SelectAllCheckbox";
import TableCaption from "@/components/TableCaption/TableCaption";
import LocalTime from "@/components/base/LocalTime/LocalTime";
import type { PaginationBarProps } from "@/components/base/PaginationBar/PaginationBar";
import PaginationBar from "@/components/base/PaginationBar/PaginationBar";
import SortIndicator from "@/components/base/SortIndicator";
import TableActions from "@/components/base/TableActions";
import TooltipButton from "@/components/base/TooltipButton/TooltipButton";
import { isDev } from "@/constants";
import { useAppLayoutContext } from "@/context";
import { useRegionDetailsContext } from "@/context/RegionDetailsContext";
import { useRowSelectionContext } from "@/context/RowSelectionContext";
import type { UseSitesQueryResult } from "@/hooks/react-query";
import { getCountryName } from "@/utils";

const createAccessor =
  <T, K extends keyof T>(keys: K[] | K) =>
  (row: T) =>
    pick(keys, row);

export type Site = SitesQueryResult["items"][number];
export type SitesColumnDef = ColumnDef<Site, Partial<Site>>;
export type SitesColumn = Column<Site, unknown>;

type SortProps = {
  sorting: SortingState;
  setSorting: Dispatch<SetStateAction<SortingState>>;
};
const SitesTable = ({
  data,
  isLoading,
  error,
  setSearchText,
  paginationProps,
  sorting,
  setSorting,
}: Pick<UseSitesQueryResult, "data" | "isLoading" | "error"> & {
  setSearchText: (text: string) => void;
  paginationProps: PaginationBarProps;
} & SortProps) => {
  const [columnVisibility, setColumnVisibility] = useLocalStorageState("sitesTableColumnVisibility", {
    defaultValue: {},
  });
  const { rowSelection, setRowSelection } = useRowSelectionContext("sites");
  const { setSelected: setRegionId } = useRegionDetailsContext();
  const { setSidebar } = useAppLayoutContext();

  // clear selection on unmount
  useEffect(() => {
    return () => setRowSelection({});
  }, [setRowSelection]);

  const columns = useMemo<SitesColumnDef[]>(
    () => [
      {
        id: "select",
        accessorKey: "name",
        enableSorting: false,
        header: ({ table }) => <SelectAllCheckbox table={table} tableId="sites" />,
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
        accessorKey: "name",
        enableSorting: true,
        accessorFn: createAccessor(["name", "url", "name_unique"]),
        header: ({ header }) => (
          <>
            <div>
              Name <SortIndicator header={header} />
            </div>
            <div className="u-text--muted">URL</div>
          </>
        ),
        cell: ({ getValue }) => {
          return (
            <>
              <div>
                {getValue().name}&nbsp;
                {!getValue().name_unique ? (
                  <TooltipButton
                    buttonProps={{ "aria-label": "warning - name is not unique" }}
                    iconName="warning"
                    iconProps={{ className: "u-no-margin--left" }}
                    message={
                      <>
                        This MAAS name is not unique in Site Manager.
                        <br />
                        You can change this name in the MAAS region itself.
                      </>
                    }
                  ></TooltipButton>
                ) : null}
              </div>
              <ExternalLink to={getValue().url || ""}>{getValue().url}</ExternalLink>
            </>
          );
        },
      },
      {
        id: "connection",
        // TODO: enable sorting once the back-end supports it for this key https://warthogs.atlassian.net/browse/MAASENG-1844
        enableSorting: false,
        accessorFn: createAccessor(["stats", "connection_status"]),
        header: ({ header }) => (
          <>
            <div className="connection__text">
              connection <SortIndicator header={header} />
            </div>
            <div className="connection__text u-text--muted">last seen</div>
          </>
        ),
        cell: ({ getValue }) => {
          const { stats, connection_status } = getValue();
          return stats && connection_status ? (
            <ConnectionInfo connection={connection_status} lastSeen={stats.last_seen} />
          ) : null;
        },
      },
      {
        id: "address",
        enableSorting: false,
        accessorFn: createAccessor(["country", "city", "zip", "street"]),
        header: ({ header }) => (
          <>
            <div>
              country <SortIndicator header={header} />
            </div>
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
        accessorKey: "timezone",
        enableSorting: false,
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
              <LocalTime timezone={timezone} />
            </div>
          ) : null;
        },
      },
      {
        id: "machines",
        // TODO: enable sorting once the back-end supports it for this key https://warthogs.atlassian.net/browse/MAASENG-1844
        enableSorting: false,
        accessorFn: createAccessor("stats"),
        header: ({ header }) => (
          <div>
            machines <SortIndicator header={header} />
          </div>
        ),
        cell: ({ getValue }) => {
          const { stats } = getValue();
          return stats ? stats.total_machines : null;
        },
      },
      {
        id: "status",
        enableSorting: false,
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
      {
        id: "actions",
        accessorKey: "id",
        accessorFn: createAccessor("id"),
        enableSorting: false,
        // Empty frag is needed here so nothing is rendered, otherwise react-table will render "ID".
        // Columns control will show here, but this is implemented below in the component body.
        header: () => <></>,
        cell: ({ getValue }) => {
          const { id } = getValue();
          return (
            <TableActions
              className="u-align--right"
              hasBorder
              onDelete={() => {
                if (id) {
                  setRowSelection({ [id]: true });
                  setSidebar("removeRegions");
                }
              }}
              onEdit={() => {
                if (id) {
                  setRegionId(id);
                  setSidebar("editRegion");
                }
              }}
            />
          );
        },
      },
    ],
    [setRegionId, setRowSelection, setSidebar],
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
      sorting,
    },
    onSortingChange: setSorting,
    getRowId: (row) => row.id,
    manualPagination: true,
    pageCount,
    onColumnVisibilityChange: setColumnVisibility,
    enableRowSelection: true,
    enableMultiRowSelection: true,
    onRowSelectionChange: setRowSelection,
    getCoreRowModel: getCoreRowModel(),
    manualSorting: true,
    enableSorting: true,
    debugTable: isDev,
    debugHeaders: isDev,
    debugColumns: isDev,
  });

  return (
    <>
      <SitesTableControls isLoading={isLoading} setSearchText={setSearchText} totalSites={data?.total ?? null} />
      <PaginationBar {...paginationProps} />
      <DynamicTable aria-label="sites" className="sites-table">
        <thead className="sites-table__head">
          {table.getHeaderGroups().map((headerGroup) => (
            <tr key={headerGroup.id}>
              {headerGroup.headers.map((header) => {
                return (
                  <th
                    className={classNames(header.column.id, {
                      "p-button--table-header": header?.column?.getCanSort(),
                    })}
                    colSpan={header.colSpan}
                    key={header.id}
                    onClick={header.column.getToggleSortingHandler()}
                  >
                    {header.isPlaceholder ? null : flexRender(header.column.columnDef.header, header.getContext())}
                    {header.column.id === "actions" ? (
                      // Make sure the columns control is rendered above the actions column
                      <div className="u-align--right">
                        <ColumnsVisibilityControl columns={table.getAllLeafColumns()} />
                      </div>
                    ) : null}
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
        ) : isLoading ? (
          <TableCaption>
            <TableCaption.Loading />
          </TableCaption>
        ) : table.getRowModel().rows.length < 1 ? (
          <NoRegions />
        ) : (
          <DynamicTable.Body>
            {table.getRowModel().rows.map((row) => {
              return (
                <tr
                  className={classNames(
                    { "sites-table-row--muted": row.original.connection_status === "unknown" },
                    "sites-table-row",
                  )}
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
          </DynamicTable.Body>
        )}
      </DynamicTable>
    </>
  );
};

export default SitesTable;
