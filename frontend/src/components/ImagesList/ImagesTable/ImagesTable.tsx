import { useMemo } from "react";

import { ContentSection } from "@canonical/maas-react-components";
import type { ColumnDef, Column } from "@tanstack/react-table";
import { useReactTable, getCoreRowModel, flexRender } from "@tanstack/react-table";

import DynamicTable from "@/components/DynamicTable/DynamicTable";
import TableCaption from "@/components/TableCaption";
import { useImagesQuery } from "@/hooks/react-query";
import type { Image } from "@/mocks/factories";

export type ImageColumnDef = ColumnDef<Image, Partial<Image>>;
export type ImageColumn = Column<Image, unknown>;

const ImagesTable = () => {
  const { data, error, isPending } = useImagesQuery({ page: 1, size: 10 });

  const columns = useMemo<ImageColumnDef[]>(
    () => [
      {
        id: "name",
        accessorKey: "name",
        enableSorting: true,
        header: () => "Name",
      },
      {
        id: "release",
        accessorKey: "release",
        enableSorting: true,
        header: () => "Release",
      },
      {
        id: "architecture",
        accessorKey: "architecture",
        enableSorting: true,
        header: () => "Architecture",
      },
      {
        id: "size",
        accessorKey: "size",
        enableSorting: true,
        header: () => "Size",
      },
      {
        id: "downloaded",
        accessorKey: "downloaded",
        enableSorting: true,
        header: () => "Downloaded",
      },
      {
        id: "number_of_sites_synced",
        accessorKey: "number_of_sites_synced",
        enableSorting: true,
        header: () => "Number of Sites Synced",
      },
      {
        id: "is_custom_image",
        accessorKey: "is_custom_image",
        enableSorting: true,
        header: () => "Is Custom Image",
      },
      {
        id: "last_synced",
        accessorKey: "last_synced",
        enableSorting: true,
        header: () => "Last Synced",
      },
    ],
    [],
  );

  const table = useReactTable<Image>({
    data: data?.items || [],
    columns,
    getRowId: (row) => `${row.id}`,
    enableSorting: true,
    getCoreRowModel: getCoreRowModel(),
  });

  return (
    <ContentSection>
      <DynamicTable aria-label="images">
        <thead>
          {table.getHeaderGroups().map((headerGroup) => (
            <tr key={headerGroup.id}>
              {headerGroup.headers.map((header) => (
                <th key={header.id} onClick={header.column.getToggleSortingHandler()}>
                  {flexRender(header.column.columnDef.header, header.getContext())}
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
          <TableCaption>
            <TableCaption.Loading />
          </TableCaption>
        ) : (
          <DynamicTable.Body>
            {table.getRowModel().rows.map((row) => (
              <tr key={row.id}>
                {row.getVisibleCells().map((cell) => (
                  <td key={cell.id}>{flexRender(cell.column.columnDef.cell, cell.getContext())}</td>
                ))}
              </tr>
            ))}
          </DynamicTable.Body>
        )}
      </DynamicTable>
    </ContentSection>
  );
};

export default ImagesTable;
