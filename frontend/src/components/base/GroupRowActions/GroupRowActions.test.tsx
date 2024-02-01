import GroupRowActions from "./GroupRowActions";

import { screen, render, userEvent } from "@/utils/test-utils";

it("calls toggleExpanded when button is clicked", async () => {
  const toggleExpanded = vi.fn();
  render(<GroupRowActions getIsExpanded={() => false} toggleExpanded={toggleExpanded} />);

  await userEvent.click(screen.getByRole("button"));
  expect(toggleExpanded).toHaveBeenCalled();
});

it('displays "Collapse" when expanded', () => {
  render(<GroupRowActions getIsExpanded={() => true} toggleExpanded={() => {}} />);
  expect(screen.getByText("Collapse")).toBeInTheDocument();
});

it('displays "Expand" when not expanded', () => {
  render(<GroupRowActions getIsExpanded={() => false} toggleExpanded={() => {}} />);
  expect(screen.getByText("Expand")).toBeInTheDocument();
});
