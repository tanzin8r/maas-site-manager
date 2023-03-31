import { vi } from "vitest";

import CopyButton from "./CopyButton";

import { render, screen, userEvent } from "@/test-utils";

it("should render a copy button", () => {
  const text = "sample-text";
  render(<CopyButton value={text} />);
  expect(screen.getByRole("button", { name: /copy/i })).toBeInTheDocument();
});

it("adds text to clipboard when clicked", async () => {
  const copyFn = vi.fn(() => Promise.resolve());
  Object.defineProperty(navigator, "clipboard", {
    value: {
      writeText: copyFn,
    },
  });

  const text = "sample-text";
  render(<CopyButton value={text} />);

  const copyBtn = screen.getByRole("button", { name: /copy/i });
  await userEvent.click(copyBtn);
  expect(copyFn).toHaveBeenCalledWith(text);
});
