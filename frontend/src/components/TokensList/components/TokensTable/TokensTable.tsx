import { useCallback, useMemo, useState } from "react";

import { Input } from "@canonical/react-components";
import type { ColumnDef, Column } from "@tanstack/react-table";
import { flexRender, useReactTable, getCoreRowModel } from "@tanstack/react-table";
import { format, formatDistanceStrict } from "date-fns";
import pick from "lodash/fp/pick";

import type { Token } from "@/api/types";
import CopyButton from "@/components/base/CopyButton";
import type { useTokensQueryResult } from "@/hooks/api";
import { copyToClipboard } from "@/utils";

const createAccessor =
  <T, K extends keyof T>(keys: K[] | K) =>
  (row: T) =>
    pick(keys, row);

export type TokenColumnDef = ColumnDef<Token, Partial<Token>>;
export type TokenColumn = Column<Token, unknown>;

const TokensTable = ({
  data,
  isFetchedAfterMount,
  isLoading,
}: Pick<useTokensQueryResult, "data" | "isLoading" | "isFetchedAfterMount">) => {
  const [copiedText, setCopiedText] = useState("");
  const isTokenCopied = useCallback((token: string) => token === copiedText, [copiedText]);

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
        header: ({ table }) => (
          <div>
            <Input
              checked={table.getIsAllRowsSelected()}
              onChange={table.getToggleAllRowsSelectedHandler()}
              type="checkbox"
              {...{
                indeterminate: table.getIsSomeRowsSelected(),
              }}
            />
          </div>
        ),
        cell: ({ row }) => (
          <div>
            <Input
              checked={row.getIsSelected()}
              disabled={!row.getCanSelect()}
              onChange={row.getToggleSelectedHandler()}
              type="checkbox"
              {...{
                indeterminate: row.getIsSomeSelected(),
              }}
            />
          </div>
        ),
      },
      {
        id: "token",
        header: () => <div>Token</div>,
        accessorFn: createAccessor("token"),
        cell: ({ getValue }) => {
          const { token } = getValue();
          return (
            <div className="token-cell" onClick={() => handleTokenCopy(token!)}>
              <span className="token-text">{token}</span>
              <CopyButton isCopied={isTokenCopied(token!)} value={token || ""} />
            </div>
          );
        },
      },
      {
        id: "expirationTime",
        accessorFn: createAccessor("expires"),
        header: () => <div>Time until expiration</div>,
        cell: ({ getValue }) => {
          const { expires } = getValue();
          return <div>{expires ? formatDistanceStrict(new Date(expires), new Date()) : null}</div>;
        },
      },
      {
        id: "created",
        accessorFn: createAccessor("created"),
        header: () => <div>Created (UTC)</div>,
        cell: ({ getValue }) => {
          const { created } = getValue();
          return <div>{created ? format(new Date(created), "yyyy-MM-dd HH:mm") : null}</div>;
        },
      },
    ],
    [handleTokenCopy, isTokenCopied],
  );
  const [rowSelection, setRowSelection] = useState({});
  const noItems = useMemo<Token[]>(() => [], []);

  const tokenTable = useReactTable<Token>({
    data: data?.items || noItems,
    columns,
    state: {
      rowSelection,
    },
    enableRowSelection: true,
    getCoreRowModel: getCoreRowModel(),
    columnResizeMode: "onChange",
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
                {header.column.getCanResize() && (
                  <div
                    className={`resizer ${header.column.getIsResizing() ? "isResizing" : ""}`}
                    onMouseDown={header.getResizeHandler()}
                    onTouchStart={header.getResizeHandler()}
                  ></div>
                )}
              </th>
            ))}
          </tr>
        ))}
      </thead>
      {isLoading && !isFetchedAfterMount ? (
        <caption>Loading...</caption>
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
      {!isLoading && data?.items.length === 0 ? (
        <caption className="empty-table-caption">
          <div className="empty-table-caption__body">
            <h2>No tokens available</h2>
            <p className="p-heading--4">Generate new tokens and follow the instructions above to enrol MAAS regions.</p>
          </div>
        </caption>
      ) : null}
    </table>
  );
};

export default TokensTable;
