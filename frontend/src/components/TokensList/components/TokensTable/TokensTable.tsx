import { useCallback, useMemo, useState } from "react";

import type { ColumnDef, Column, Row, Getter } from "@tanstack/react-table";
import { flexRender, useReactTable, getCoreRowModel } from "@tanstack/react-table";
import pick from "lodash/fp/pick";

import type { Token } from "@/api/types";
import SelectAllCheckbox from "@/components/SelectAllCheckbox";
import TableCaption from "@/components/TableCaption";
import CopyButton from "@/components/base/CopyButton";
import TooltipButton from "@/components/base/TooltipButton";
import { useRowSelectionContext } from "@/context/RowSelectionContext";
import type { useTokensQueryResult } from "@/hooks/react-query";
import { copyToClipboard, formatDistanceToNow, formatUTCDateString } from "@/utils";

const createAccessor =
  <T, K extends keyof T>(keys: K[] | K) =>
  (row: T) =>
    pick(keys, row);

export type TokenColumnDef = ColumnDef<Token, Partial<Token>>;
export type TokenColumn = Column<Token, unknown>;

const TokensTable = ({ data, error, isLoading }: Pick<useTokensQueryResult, "data" | "error" | "isLoading">) => {
  const [copiedText, setCopiedText] = useState("");

  const { rowSelection, setRowSelection } = useRowSelectionContext("tokens");
  const isTokenCopied = useCallback((token: string) => token === copiedText, [copiedText]);

  // clear table selection on unmount
  useEffect(() => {
    return () => setRowSelection({});
  }, [setRowSelection]);

  const resetCopiedText = (timeout = 500) => {
    setTimeout(() => {
      setCopiedText("");
    }, timeout);
  };

  const handleTokenCopy = useCallback((token: string) => {
    copyToClipboard(token, setCopiedText);
    resetCopiedText();
  }, []);

  const columns = useMemo<TokenColumnDef[]>(
    () => [
      {
        id: "select",
        accessorKey: "value",
        header: ({ table }) => <SelectAllCheckbox table={table} tableId="tokens" />,
        cell: ({ row, getValue }: { row: Row<Token>; getValue: Getter<Token["value"]> }) => (
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
        ),
      },
      {
        id: "token",
        header: () => <div>Token</div>,
        accessorFn: createAccessor("value"),
        cell: ({ getValue }) => {
          const { value } = getValue();
          return (
            <div className="token-cell" onClick={() => handleTokenCopy(value!)}>
              <span className="token-text">{value}</span>
              <CopyButton isCopied={isTokenCopied(value!)} value={value || ""} />
            </div>
          );
        },
      },
      {
        id: "expirationTime",
        accessorFn: createAccessor("expired"),
        header: () => <div>Time until expiration</div>,
        cell: ({ getValue }) => {
          const { expired } = getValue();
          return (
            <TooltipButton message={expired ? `${formatUTCDateString(expired)} (UTC)` : null} position="btm-center">
              {expired ? formatDistanceToNow(expired) : null}
            </TooltipButton>
          );
        },
      },
      {
        id: "created",
        accessorFn: createAccessor("created"),
        header: () => <div>Created (UTC)</div>,
        cell: ({ getValue }) => {
          const { created } = getValue();
          return <div>{created ? formatUTCDateString(created) : null}</div>;
        },
      },
    ],
    [handleTokenCopy, isTokenCopied],
  );

  const noItems = useMemo<Token[]>(() => [], []);

  const tokenTable = useReactTable<Token>({
    data: data?.items || noItems,
    columns,
    state: {
      rowSelection,
    },
    getRowId: (row) => `${row.id}`,
    manualPagination: true,
    enableRowSelection: true,
    getCoreRowModel: getCoreRowModel(),
    enableMultiRowSelection: true,
    onRowSelectionChange: setRowSelection,
  });
  return (
    <table aria-label="tokens" className="tokens-table">
      <thead>
        {tokenTable.getHeaderGroups().map((headerGroup) => (
          <tr key={headerGroup.id}>
            {headerGroup.headers.map((header) => (
              <th colSpan={header.colSpan} key={header.id}>
                {header.isPlaceholder ? null : flexRender(header.column.columnDef.header, header.getContext())}
              </th>
            ))}
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
      ) : tokenTable.getRowModel().rows.length < 1 ? (
        <TableCaption>
          <TableCaption.Title>No tokens available</TableCaption.Title>
          <TableCaption.Description>
            Generate new tokens and follow the instructions above to enrol MAAS regions.
          </TableCaption.Description>
        </TableCaption>
      ) : (
        <tbody>
          {tokenTable.getRowModel().rows.map((row) => (
            <tr key={row.id}>
              {row.getVisibleCells().map((cell) => {
                return <td key={cell.id}>{flexRender(cell.column.columnDef.cell, cell.getContext())}</td>;
              })}
            </tr>
          ))}
        </tbody>
      )}
    </table>
  );
};

export default TokensTable;
