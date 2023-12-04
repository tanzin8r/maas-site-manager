import type { ReactNode } from "react";

import classNames from "classnames";

type Props = {
  className?: string;
  isPending?: boolean;
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

const Placeholder = ({ text, children, className, isPending = false }: Props) => {
  const delay = Math.floor(Math.random() * 750);
  if (isPending) {
    return (
      <span
        aria-label="loading"
        className={classNames("p-placeholder", className)}
        role="progressbar"
        style={{ animationDelay: `${delay}ms` }}
      >
        <span aria-hidden="true">{text || children}</span>
      </span>
    );
  }
  return <>{children}</>;
};

export default Placeholder;
