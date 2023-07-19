import TooltipButton from "./TooltipButton";

import { userEvent, render, screen } from "@/test-utils";

it("renders with default options correctly", async () => {
  const message = "Hi, I'm a tooltip!";
  render(<TooltipButton message={message} />);

  const button = screen.getByRole("button");
  await userEvent.click(button);

  expect(screen.getByRole("tooltip")).toHaveTextContent(message);
});

it("can override default props", async () => {
  const message = "Hi, I'm a tooltip!";
  render(
    <TooltipButton
      buttonProps={{ appearance: "negative", className: "button-class" }}
      data-testid="tooltip-portal"
      iconName="warning"
      iconProps={{ className: "icon-class", "data-testid": "icon" }}
      message={message}
      tooltipClassName="tooltip-class"
    />,
  );

  const button = screen.getByRole("button");
  await userEvent.click(button);

  expect(button).toHaveClass("p-button--negative has-icon button-class");
  expect(screen.getByTestId("icon")).toHaveClass("icon-class p-icon--warning");
  expect(screen.getByTestId("tooltip-portal")).toHaveClass("p-tooltip--btm-left is-detached tooltip-class");
});
