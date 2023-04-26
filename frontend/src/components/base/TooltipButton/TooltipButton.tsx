import type { ReactNode } from "react";

import type { ButtonProps, IconProps, SubComponentProps, TooltipProps } from "@canonical/react-components";
import { Button, Icon, Tooltip } from "@canonical/react-components";

type Props = Omit<TooltipProps, "aria-label" | "children"> & {
  "aria-label"?: ButtonProps["aria-label"];
  buttonProps?: SubComponentProps<Omit<ButtonProps, "aria-label">>;
  children?: ReactNode;
  iconName?: IconProps["name"];
  iconProps?: SubComponentProps<Omit<IconProps, "name">>;
};

const TooltipButton = ({
  "aria-label": ariaLabel,
  buttonProps,
  children,
  iconName = "information",
  iconProps,
  message,
  ...tooltipProps
}: Props): JSX.Element => {
  return (
    <Tooltip message={message} {...tooltipProps}>
      <Button
        appearance="link"
        aria-label={ariaLabel}
        className="tooltip-button u-no-border u-no-padding u-no-margin u-align--left"
        hasIcon
        type="button"
        {...buttonProps}
      >
        {children}
        {iconName ? <Icon name={iconName} {...iconProps} /> : null}
      </Button>
    </Tooltip>
  );
};

export default TooltipButton;
