import RemoveRegions from "./index";

import { render, screen, userEvent } from "@/test-utils";

vi.mock("@/context", async () => {
  const actual = await vi.importActual("@/context");
  return {
    ...actual!,
    useRowSelectionContext: () => ({
      rowSelection: {
        "1": true,
        "2": true,
      },
    }),
  };
});

it("submit button should not be disabled when something has been typed", async () => {
  render(<RemoveRegions />);
  const errorMessage = /Confirmation string is not correct/i;
  await expect(screen.getByRole("button", { name: /Remove/i })).toBeDisabled();
  await userEvent.type(screen.getByRole("textbox"), "invalid text");
  expect(screen.queryByText(errorMessage)).not.toBeInTheDocument();
  await expect(screen.getByRole("button", { name: /Remove/i })).toBeEnabled();
});

it("validation error is shown after user attempts submission", async () => {
  render(<RemoveRegions />);
  const errorMessage = /Confirmation string is not correct/i;
  await userEvent.type(screen.getByRole("textbox"), "incorrect string{tab}");
  expect(screen.queryByText(errorMessage)).not.toBeInTheDocument();
  await userEvent.click(screen.getByRole("button", { name: /Remove/i }));
  expect(screen.getByText(errorMessage)).toBeInTheDocument();
});

it("does not display error message on blur if the value has not chagned", async () => {
  render(<RemoveRegions />);
  await expect(screen.getByRole("button", { name: /Remove/i })).toBeDisabled();
  await userEvent.type(screen.getByRole("textbox"), "{tab}");
  expect(screen.queryByText(/Confirmation string is not correct/i)).not.toBeInTheDocument();
  await expect(screen.getByRole("button", { name: /Remove/i })).toBeDisabled();
});

it("validation error is hidden on change if the user already attempted submission", async () => {
  render(<RemoveRegions />);
  const errorMessage = /Confirmation string is not correct/i;
  await userEvent.type(screen.getByRole("textbox"), "incorrect string");
  await userEvent.click(screen.getByRole("button", { name: /Remove/i }));
  expect(screen.getByText(errorMessage)).toBeInTheDocument();
  await userEvent.clear(screen.getByRole("textbox"));
  await userEvent.type(screen.getByRole("textbox"), "remove 2 regions");
  expect(screen.queryByText(errorMessage)).not.toBeInTheDocument();
});
