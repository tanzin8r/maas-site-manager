import type { MouseEventHandler } from "react";

import { Button, Icon } from "@canonical/react-components";

type Props = {
  disabled?: boolean;
  label?: string;
  onClick?: MouseEventHandler<HTMLButtonElement>;
  showDeleteIcon?: boolean;
  type?: HTMLButtonElement["type"];
};

const RemoveButton = ({ disabled, label = "Remove", onClick, showDeleteIcon, type }: Props) => {
  return (
    <Button appearance="negative" className="remove-btn" disabled={disabled} onClick={onClick} type={type}>
      {showDeleteIcon && (
        <>
          <Icon light name="delete" />{" "}
        </>
      )}
      {label}
    </Button>
  );
};

export default RemoveButton;
