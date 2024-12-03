import type { PropsWithChildren } from "react";
import React, { createContext, useContext, useState } from "react";

import { usePrevious } from "@canonical/react-components";
import type { OnChangeFn, RowSelectionState } from "@tanstack/react-table";

export type TableId = "sites" | "requests" | "tokens" | "images";
type RowSelectionContextValue = {
  rowSelection: RowSelectionState;
  setRowSelection: OnChangeFn<RowSelectionState>;
  clearRowSelection: () => void;
};
const ContextsCache = new Map<TableId, React.Context<RowSelectionContextValue>>();

const getRowSelectionContext = (id: TableId): React.Context<RowSelectionContextValue> => {
  if (!ContextsCache.has(id)) {
    ContextsCache.set(
      id,
      createContext<RowSelectionContextValue>({
        rowSelection: {},
        setRowSelection: () => ({}),
        clearRowSelection: () => ({}),
      }),
    );
  }
  return ContextsCache.get(id)!;
};

export const useRowSelectionContext = (id: TableId): RowSelectionContextValue => {
  const RowSelectionContext = getRowSelectionContext(id);
  return useContext(RowSelectionContext);
};

type UseRowSelectionOptions = {
  clearOnUnmount?: boolean;
  currentPage?: number;
  pageSize?: number;
};

export const useRowSelection = (id: TableId, options?: UseRowSelectionOptions): RowSelectionContextValue => {
  const { clearOnUnmount = false, currentPage = 1, pageSize = 50 } = options || {};
  const context = useRowSelectionContext(id);
  const previousPage = usePrevious(currentPage);
  const previousPageSize = usePrevious(pageSize);

  useEffect(() => {
    return () => {
      if (clearOnUnmount) {
        context.setRowSelection({});
      }
    };
    // explicitly omitting context from dependencies
    // to ensure this clears row selection only on unmount
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [clearOnUnmount]);

  // Clear row selection on page change
  useEffect(() => {
    if (currentPage !== previousPage) {
      context.clearRowSelection();
    }
  }, [currentPage, previousPage, context]);

  // Clear row selection on page size change
  useEffect(() => {
    if (pageSize !== previousPageSize) {
      context.clearRowSelection();
    }
  }, [pageSize, previousPageSize, context]);

  return context;
};

export const getRowSelectionContextProvider =
  (id: TableId, value = {}) =>
  ({ children }: PropsWithChildren) => {
    const RowSelectionContext = getRowSelectionContext(id);
    const [rowSelection, setRowSelection] = useState(value);
    const clearRowSelection = () => setRowSelection({});

    return (
      <RowSelectionContext.Provider value={{ rowSelection, setRowSelection, clearRowSelection }}>
        {children}
      </RowSelectionContext.Provider>
    );
  };

const SitesRowSelectionContextProvider = getRowSelectionContextProvider("sites");
const RequestsRowSelectionContextProvider = getRowSelectionContextProvider("requests");
const TokensRowSelectionContextProvider = getRowSelectionContextProvider("tokens");
export const ImagesRowSelectionContextProvider = getRowSelectionContextProvider("images");

export const RowSelectionContextProviders = ({ children }: PropsWithChildren) => {
  return (
    <SitesRowSelectionContextProvider>
      <RequestsRowSelectionContextProvider>
        <TokensRowSelectionContextProvider>
          <ImagesRowSelectionContextProvider>{children}</ImagesRowSelectionContextProvider>
        </TokensRowSelectionContextProvider>
      </RequestsRowSelectionContextProvider>
    </SitesRowSelectionContextProvider>
  );
};
