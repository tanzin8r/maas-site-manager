import { useMemo } from "react";

import { Button } from "@canonical/react-components";
import type {
  ColumnDef,
  Column,
  GroupingState,
  SortingState,
  OnChangeFn,
  ExpandedState,
  Row,
  Header,
} from "@tanstack/react-table";
import {
  useReactTable,
  getCoreRowModel,
  getGroupedRowModel,
  flexRender,
  getExpandedRowModel,
} from "@tanstack/react-table";
import classNames from "classnames";

import "./ImagesTable.scss";
import useImagesTableColumns from "./useImagesTableColumns";

import type { Image } from "@/api";
import type { ImagesSortKey, SortBy } from "@/api/handlers";
import DynamicTable from "@/components/DynamicTable";
import TableCaption from "@/components/TableCaption";
import SortIndicator from "@/components/base/SortIndicator";
import { useAppLayoutContext, useRowSelection } from "@/context";
import { useImagesInfiniteQuery } from "@/hooks/react-query";
import { getSortBy } from "@/utils";
export type ImageColumnDef = ColumnDef<Image, Partial<Image>>;
export type ImageColumn = Column<Image, unknown>;

type UseImagesQueryResult = ReturnType<typeof useImagesInfiniteQuery>;
export type ImagesTableProps = {
  data?: UseImagesQueryResult["data"];
  error?: UseImagesQueryResult["error"];
  isPending: UseImagesQueryResult["isPending"];
  setSidebar: ReturnType<typeof useAppLayoutContext>["setSidebar"];
  rowSelection: ReturnType<typeof useRowSelection>["rowSelection"];
  setRowSelection: ReturnType<typeof useRowSelection>["setRowSelection"];
  sorting: SortingState;
  setSorting: OnChangeFn<SortingState>;
};

// Filter out the name column from the header
const filterHeaders = (header: Header<Image, unknown>) => header.column.id !== "name";
// Filter out the name column from individual cells
const filterCells = (row: Row<Image>, column: Column<Image, unknown>) => {
  if (row.getIsGrouped()) {
    return ["select", "name", "action"].includes(column.id);
  } else {
    return column.id !== "name";
  }
};

export const ImagesTable: React.FC<ImagesTableProps> = ({
  data,
  error,
  isPending,
  setSidebar,
  rowSelection,
  setRowSelection,
  sorting,
  setSorting,
}) => {
  const columns = useImagesTableColumns();
  const noItems = useMemo<Image[]>(() => [], []);

  const [grouping, setGrouping] = useState<GroupingState>(["name"]);
  const [expanded, setExpanded] = useState<ExpandedState>(true);

  const table = useReactTable<Image>({
    data: data?.items ? data.items : noItems,
    columns,
    state: {
      rowSelection,
      grouping,
      expanded,
      sorting,
    },
    manualPagination: true,
    autoResetExpanded: false,
    onExpandedChange: setExpanded,
    onSortingChange: setSorting,
    onGroupingChange: setGrouping,
    manualSorting: true,
    enableSorting: true,
    enableExpanding: true,
    getExpandedRowModel: getExpandedRowModel(),
    getCoreRowModel: getCoreRowModel(),
    getGroupedRowModel: getGroupedRowModel(),
    groupedColumnMode: false,
    enableRowSelection: true,
    enableMultiRowSelection: true,
    onRowSelectionChange: setRowSelection,
    getRowId: (row) => `${row.id}`,
  });

  return (
    <DynamicTable aria-label="images" className="p-table-dynamic--with-select images-table">
      <thead>
        {table.getHeaderGroups().map((headerGroup) => (
          <tr key={headerGroup.id}>
            {headerGroup.headers.filter(filterHeaders).map((header) => (
              <th className={classNames(`${header.column.id}`)} key={header.id}>
                {header.column.getCanSort() ? (
                  <Button
                    appearance="link"
                    className="p-button--table-header"
                    onClick={header.column.getToggleSortingHandler()}
                    type="button"
                  >
                    {flexRender(header.column.columnDef.header, header.getContext())}
                    <SortIndicator header={header} />
                  </Button>
                ) : (
                  flexRender(header.column.columnDef.header, header.getContext())
                )}
              </th>
            ))}
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
          <TableCaption.Title>No images</TableCaption.Title>
          <TableCaption.Description>
            There are no images stored in Site Manager at the moment. You can either upload images, or connect to an
            upstream image source to download images from.
          </TableCaption.Description>
          <TableCaption.Description>
            <Button onClick={() => setSidebar("uploadImage")}>Upload image</Button>
            <Button onClick={() => setSidebar("downloadImages")}>Download images</Button>
          </TableCaption.Description>
        </TableCaption>
      ) : (
        <DynamicTable.Body>
          {table.getRowModel().rows.map((row) => {
            const { getIsGrouped, id, index, getVisibleCells } = row;
            const isIndividualRow = !getIsGrouped();
            return (
              <tr
                className={classNames({
                  "individual-row": isIndividualRow,
                  "group-row": !isIndividualRow,
                })}
                key={id + index}
              >
                {getVisibleCells()
                  .filter((cell) => filterCells(row, cell.column))
                  .map((cell) => {
                    const { column, id: cellId } = cell;
                    return (
                      <td className={classNames(`${cell.column.id}`)} key={cellId}>
                        {flexRender(column.columnDef.cell, cell.getContext())}
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

export const ImagesTableContainer = () => {
  const { setSidebar } = useAppLayoutContext();
  const { rowSelection, setRowSelection } = useRowSelection("images", { clearOnUnmount: true });
  const [sorting, setSorting] = useState<SortingState>([{ id: "name", desc: false }]);
  const sortBy = getSortBy(sorting) as SortBy<ImagesSortKey>;
  const { data, error, isPending } = useImagesInfiniteQuery({ sortBy });

  return (
    <ImagesTable
      data={data}
      error={error}
      isPending={isPending}
      rowSelection={rowSelection}
      setRowSelection={setRowSelection}
      setSidebar={setSidebar}
      setSorting={setSorting}
      sorting={sorting}
    />
  );
};

export default ImagesTableContainer;
