import type { ReactNode, CSSProperties } from "react";

import classNames from "classnames";

type Props = {
  className?: string;
  isPending?: boolean;
  style?: CSSProperties;
} & (
  | {
      text?: never;
      children?: ReactNode;
    }
  | {
      text?: string;
      children?: never;
    }
);

const Placeholder = ({ text, children, className, isPending = false, style }: Props) => {
  const delay = Math.floor(Math.random() * 750);
  if (isPending) {
    return (
      <span
        aria-label="loading"
        className={classNames("p-placeholder", className)}
        role="progressbar"
        style={{ animationDelay: `${delay}ms`, ...style }}
      >
        <span aria-hidden="true">{text || children || "Loading"}</span>
      </span>
    );
  }
  return <>{children}</>;
};

export default Placeholder;
