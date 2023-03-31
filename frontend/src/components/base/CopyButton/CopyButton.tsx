import { useState } from "react";

import { Button } from "@canonical/react-components";
import classNames from "classnames";

import { copyToClipboard } from "@/utils";

type CopyButtonProps = {
  value: string;
  onClick?: () => void;
  isCopied?: boolean;
};

const CopyButton = ({ value, onClick, isCopied }: CopyButtonProps) => {
  const [copiedText, setCopiedText] = useState("");
  const isTextCopied = !!copiedText || isCopied;

  const resetCopiedText = (timeout = 500) => {
    setTimeout(() => {
      setCopiedText("");
    }, timeout);
  };

  const handleCopy = () => {
    copyToClipboard(value, setCopiedText);
    resetCopiedText();
  };

  const handleOnClick = () => {
    if (onClick) {
      onClick();
    }
  };

  return (
    <Button
      className={classNames("table-cell__copy-button", { "is-copied": isTextCopied })}
      onClick={onClick ? handleOnClick : handleCopy}
      small
    >
      {isTextCopied ? "copied" : "copy"}
    </Button>
  );
};

export default CopyButton;
