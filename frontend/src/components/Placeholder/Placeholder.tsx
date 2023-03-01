import type { ReactNode } from "react";

import classNames from "classnames";

import "./Placeholder.scss";

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
        aria-hidden={true}
        className={classNames("p-placeholder", className)}
        data-testid="placeholder"
        style={{ animationDelay: `${delay}ms` }}
      >
        {text || children}
      </span>
    );
  }
  return <>{children}</>;
};

export default Placeholder;
