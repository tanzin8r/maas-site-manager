import TableActions from "./TableActions";

import { renderWithMemoryRouter, screen } from "@/utils/test-utils";

it("displays edit table action when onEdit prop is provided", () => {
  renderWithMemoryRouter(<TableActions onEdit={vi.fn()} />);

  expect(screen.getByRole("button", { name: /edit/i })).toBeInTheDocument();
});

it("displays delete table action when onDelete prop is provided", () => {
  renderWithMemoryRouter(<TableActions onDelete={vi.fn()} />);

  expect(screen.getByRole("button", { name: /delete/i })).toBeInTheDocument();
});
