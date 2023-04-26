import { useCallback, useMemo, useState } from "react";

import type { ColumnDef, Column, Row, Getter } from "@tanstack/react-table";
import { flexRender, useReactTable, getCoreRowModel } from "@tanstack/react-table";
import { format, formatDistanceStrict } from "date-fns";
import pick from "lodash/fp/pick";

import type { Token } from "@/api/types";
import SelectAllCheckbox from "@/components/SelectAllCheckbox";
import CopyButton from "@/components/base/CopyButton";
import TooltipButton from "@/components/base/TooltipButton";
import { useAppContext } from "@/context";
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
  const { rowSelection, setRowSelection } = useAppContext();
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
        accessorKey: "token",
        header: ({ table }) => <SelectAllCheckbox table={table} />,
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
        accessorFn: createAccessor("expires"),
        header: () => <div>Time until expiration</div>,
        cell: ({ getValue }) => {
          const { expires } = getValue();
          return (
            <TooltipButton
              iconName=""
              message={expires ? `${format(new Date(expires), "yyyy-MM-dd HH:mm")} (UTC)` : null}
              position="btm-center"
            >
              {expires ? formatDistanceStrict(new Date(expires), new Date()) : null}
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
          return <div>{created ? format(new Date(created), "yyyy-MM-dd HH:mm") : null}</div>;
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
    getRowId: (row) => row.id,
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
