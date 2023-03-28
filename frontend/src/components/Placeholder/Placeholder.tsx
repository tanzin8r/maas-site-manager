import type { ReactNode } from "react";

import classNames from "classnames";

type Props = {
  className?: string;
  isLoading?: boolean;
} & (
  | {
      text?: never;
      children: ReactNode;
    }
  | {
      text: string;
      children?: never;
    }
);

const Placeholder = ({ text, children, className, isLoading = false }: Props) => {
  const delay = Math.floor(Math.random() * 750);
  if (isLoading) {
    return (
      <span
        aria-label="loading"
        className={classNames("p-placeholder", className)}
        style={{ animationDelay: `${delay}ms` }}
      >
        <span aria-hidden="true">{text || children}</span>
      </span>
    );
  }
  return <>{children}</>;
};

export default Placeholder;
