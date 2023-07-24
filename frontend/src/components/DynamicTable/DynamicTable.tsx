import type { PropsWithChildren, RefObject } from "react";
import { useState, useEffect, useLayoutEffect } from "react";

import classNames from "classnames";

import BREAKPOINTS from "@/config/breakpoints";

const DynamicTable = ({ className, children, ...props }: PropsWithChildren<{ className?: string }>) => {
  return (
    <table {...props} className={classNames("p-table--dynamic", className)}>
      {children}
    </table>
  );
};

/**
 * sets a fixed height for the table body
 * allowing it to be scrolled independently of the page
 */
const DynamicTableBody = ({ className, children }: PropsWithChildren<{ className?: string }>) => {
  const tableBodyRef: RefObject<HTMLTableSectionElement> = useRef(null);
  const [offset, setOffset] = useState<number | null>(null);

  const handleResize = useCallback(() => {
    if (window.innerWidth > BREAKPOINTS.small) {
      const top = tableBodyRef.current?.getBoundingClientRect?.().top;
      if (top) setOffset(top + 1);
    } else {
      setOffset(null);
    }
  }, []);

  useLayoutEffect(() => {
    handleResize();
  }, [handleResize]);

  useEffect(() => {
    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, [handleResize]);

  return (
    <tbody
      className={className}
      ref={tableBodyRef}
      style={offset ? { height: `calc(100vh - ${offset}px)`, minHeight: `calc(100vh - ${offset}px)` } : undefined}
    >
      {children}
    </tbody>
  );
};
DynamicTable.Body = DynamicTableBody;

export default DynamicTable;
