import type { PropsWithChildren } from "react";
import React, { createContext, useContext, useState } from "react";

import type { OnChangeFn, RowSelectionState } from "@tanstack/react-table";

export type TableId = "sites" | "requests" | "tokens";
type RowSelectionContextValue = { rowSelection: RowSelectionState; setRowSelection: OnChangeFn<RowSelectionState> };
const ContextsCache = new Map<TableId, React.Context<RowSelectionContextValue>>();

const getRowSelectionContext = (id: TableId): React.Context<RowSelectionContextValue> => {
  if (!ContextsCache.has(id)) {
    ContextsCache.set(
      id,
      createContext<RowSelectionContextValue>({
        rowSelection: {},
        setRowSelection: () => ({}),
      }),
    );
  }
  return ContextsCache.get(id)!;
};

export const useRowSelectionContext = (id: TableId): RowSelectionContextValue => {
  const RowSelectionContext = getRowSelectionContext(id);
  return useContext(RowSelectionContext);
};

export const getRowSelectionContextProvider =
  (id: TableId) =>
  ({ children }: PropsWithChildren) => {
    const RowSelectionContext = getRowSelectionContext(id);
    const [rowSelection, setRowSelection] = useState({});

    return (
      <RowSelectionContext.Provider value={{ rowSelection, setRowSelection }}>{children}</RowSelectionContext.Provider>
    );
  };

const SitesRowSelectionContextProvider = getRowSelectionContextProvider("sites");
const RequestsRowSelectionContextProvider = getRowSelectionContextProvider("requests");
const TokensRowSelectionContextProvider = getRowSelectionContextProvider("tokens");

export const RowSelectionContextProviders = ({ children }: PropsWithChildren) => {
  return (
    <SitesRowSelectionContextProvider>
      <RequestsRowSelectionContextProvider>
        <TokensRowSelectionContextProvider>{children}</TokensRowSelectionContextProvider>
      </RequestsRowSelectionContextProvider>
    </SitesRowSelectionContextProvider>
  );
};
