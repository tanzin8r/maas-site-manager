import NavigationList from "./NavigationList";

import type { NavItem } from "@/components/Navigation/types";
import { renderWithMemoryRouter, screen } from "@/utils/test-utils";

it("can render an item", () => {
  const navItems: NavItem[] = [
    {
      label: "Sites",
      url: "/sites",
      icon: "machines",
    },
  ];

  renderWithMemoryRouter(<NavigationList items={navItems} onClick={vi.fn()} path={"/"} />);

  expect(screen.getByRole("list")).toBeInTheDocument();
  expect(screen.getByRole("link", { name: "Sites" })).toHaveAttribute("href", "/sites");
});

it("can render a group", () => {
  const navItems: NavItem[] = [
    {
      groupTitle: "Group 1",
      navLinks: [
        {
          url: "/sites",
          label: "Sites",
        },
      ],
    },
  ];

  renderWithMemoryRouter(<NavigationList items={navItems} onClick={vi.fn()} path={"/"} />);

  expect(screen.getAllByRole("list")).toHaveLength(2);
  expect(screen.getByText("Group 1")).toBeInTheDocument();
  expect(screen.getByRole("link", { name: "Sites" })).toHaveAttribute("href", "/sites");
});
