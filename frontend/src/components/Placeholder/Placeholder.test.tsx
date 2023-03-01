import { render, screen } from "../../test-utils";

import Placeholder from "./Placeholder";

describe("Placeholder", () => {
  it("always hides placeholder text passed as a text prop", () => {
    const { rerender } = render(<Placeholder text="Placeholder text" />);
    expect(screen.queryByText(/Placeholder text/)).not.toBeInTheDocument();
    rerender(<Placeholder isLoading text="Placeholder text" />);
    expect(screen.queryByText(/Placeholder text/)).toHaveAttribute("aria-hidden", "true");
  });

  it("hides the children when loading", () => {
    const { rerender } = render(<Placeholder>Placeholder children</Placeholder>);
    expect(screen.getByText(/Placeholder children/)).toBeInTheDocument();
    rerender(<Placeholder isLoading>Placeholder children</Placeholder>);
    expect(screen.queryByText(/Placeholder children/)).toHaveAttribute("aria-hidden", "true");
  });

  it("does not return placeholder styles when isLoading is false", () => {
    const { rerender } = render(<Placeholder>Placeholder children</Placeholder>);
    expect(screen.queryByTestId("placeholder")).not.toBeInTheDocument();
    rerender(<Placeholder isLoading>Placeholder children</Placeholder>);
    expect(screen.getByTestId("placeholder")).toBeInTheDocument();
  });
});
