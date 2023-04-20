import { MemoryRouter } from "react-router-dom";

import Navigation, { navItems, settingsNavItems } from "./Navigation";

import { render, renderWithMemoryRouter, screen, userEvent } from "@/test-utils";

describe("Navigation", () => {
  it("displays navigation", () => {
    render(
      <MemoryRouter initialEntries={[{ pathname: "/", key: "testKey" }]}>
        <Navigation />
      </MemoryRouter>,
    );
    expect(screen.getByRole("navigation")).toBeInTheDocument();
  });

  [...navItems, ...settingsNavItems].forEach(({ label, url }) => {
    it(`highlights ${label} navigation item when active`, () => {
      render(
        <MemoryRouter initialEntries={[{ pathname: url, key: "testKey" }]}>
          <Navigation />
        </MemoryRouter>,
      );

      const currentMenuItem = screen.getByRole("link", { current: "page", name: label });
      expect(currentMenuItem).toBeInTheDocument();
    });
  });

  // TODO: enable once side navigation secondary panel is implemented
  // https://warthogs.atlassian.net/browse/MAASENG-1508
  it.skip("highlights 'Settings' when active", () => {
    const { rerender } = render(
      <MemoryRouter initialEntries={[{ pathname: "/tokens", key: "testKey" }]}>
        <Navigation />
      </MemoryRouter>,
    );

    let currentMenuItem = screen.getAllByRole("link", { current: "page" })[0];
    expect(currentMenuItem).toBeInTheDocument();
    expect(currentMenuItem).toHaveTextContent("Settings");

    rerender(
      <MemoryRouter initialEntries={[{ pathname: "/requests", key: "testKey" }]}>
        <Navigation />
      </MemoryRouter>,
    );

    currentMenuItem = screen.getAllByRole("link", { current: "page" })[0];
    expect(currentMenuItem).toBeInTheDocument();
    expect(currentMenuItem).toHaveTextContent("Settings");

    rerender(
      <MemoryRouter initialEntries={[{ pathname: "/users", key: "testKey" }]}>
        <Navigation />
      </MemoryRouter>,
    );

    currentMenuItem = screen.getAllByRole("link", { current: "page" })[0];
    expect(currentMenuItem).toBeInTheDocument();
    expect(currentMenuItem).toHaveTextContent("Settings");
  });

  it("is collapsed by default", () => {
    render(
      <MemoryRouter initialEntries={[{ pathname: "/", key: "testKey" }]}>
        <Navigation />
      </MemoryRouter>,
    );
    expect(screen.getByRole("navigation")).toHaveClass("is-collapsed");
  });

  it("persists collapsed state", async () => {
    const { rerender } = render(
      <MemoryRouter initialEntries={[{ pathname: "/", key: "testKey" }]}>
        <Navigation />
      </MemoryRouter>,
    );

    const primaryNavigation = screen.getByRole("navigation");
    await userEvent.click(screen.getByRole("button", { name: "expand main navigation" }));
    expect(primaryNavigation).toHaveClass("is-pinned");

    rerender(
      <MemoryRouter initialEntries={[{ pathname: "/", key: "testKey" }]}>
        <Navigation />
      </MemoryRouter>,
    );

    expect(primaryNavigation).toHaveClass("is-pinned");
  });

  it("links to the documentation at the bottom of the nav", () => {
    renderWithMemoryRouter(<Navigation />);

    expect(screen.getByRole("link", { name: "Documentation" })).toHaveAttribute("href", "https://maas.io/docs");
  });

  it("links to MAAS discourse at the bottom of the nav", () => {
    renderWithMemoryRouter(<Navigation />);

    expect(screen.getByRole("link", { name: "Community" })).toHaveAttribute("href", "https://discourse.maas.io/");
  });

  it.skip("links to the bug report page at the bottom of the nav", () => {
    // TODO: Enable this test once a bug report link is available https://warthogs.atlassian.net/browse/MAASENG-1588
    renderWithMemoryRouter(<Navigation />);

    expect(screen.getByRole("link", { name: "Report a bug" })).toHaveAttribute("href", "");
  });

  it("removes focus from the current element after clicking the link", async () => {
    render(
      <MemoryRouter initialEntries={[{ pathname: "/", key: "testKey" }]}>
        <Navigation />
      </MemoryRouter>,
    );
    const navigationLinks = screen.getAllByRole("link");
    for (const link of navigationLinks) {
      await userEvent.click(link);
      expect(link).not.toHaveFocus();
    }
  });
});
