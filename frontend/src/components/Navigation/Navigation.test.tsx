import { rest } from "msw";
import { setupServer } from "msw/node";

import Navigation, { navItemsBottom, navItems, settingsNavItems } from "./Navigation";

import urls from "@/api/urls";
import { createMockCurrentUserResolver } from "@/mocks/resolvers";
import { renderWithMemoryRouter, screen, userEvent } from "@/test-utils";

const mockServer = setupServer(rest.get(urls.currentUser, createMockCurrentUserResolver()));

beforeAll(() => {
  mockServer.listen();
});
afterEach(() => {
  mockServer.resetHandlers();
});
afterAll(() => {
  mockServer.close();
});

describe("Navigation", () => {
  it("displays navigation", () => {
    renderWithMemoryRouter(<Navigation isLoggedIn />);
    expect(screen.getByRole("navigation")).toBeInTheDocument();
  });

  [...navItems, ...settingsNavItems].forEach(({ label, url }) => {
    it(`highlights ${label} navigation item when active`, () => {
      renderWithMemoryRouter(<Navigation isLoggedIn />, { initialEntries: [{ pathname: url, key: "testKey" }] });

      const currentMenuItem = screen.getByRole("link", { current: "page", name: label });
      expect(currentMenuItem).toBeInTheDocument();
    });
  });

  it("is collapsed by default", async () => {
    renderWithMemoryRouter(<Navigation isLoggedIn />);
    await expect(screen.getByRole("navigation")).toHaveClass("is-collapsed");
  });

  it("persists collapsed state", async () => {
    const { rerender } = renderWithMemoryRouter(<Navigation isLoggedIn />);

    const primaryNavigation = screen.getByRole("navigation");
    await userEvent.click(screen.getByRole("button", { name: "expand main navigation" }));
    await expect(primaryNavigation).toHaveClass("is-pinned");

    rerender(<Navigation isLoggedIn />);

    await expect(primaryNavigation).toHaveClass("is-pinned");
  });

  it("links to the documentation at the bottom of the nav", async () => {
    renderWithMemoryRouter(<Navigation isLoggedIn />);

    await expect(screen.getByRole("link", { name: "Documentation" })).toHaveAttribute("href", "https://maas.io/docs");
  });

  it("links to MAAS discourse at the bottom of the nav", async () => {
    renderWithMemoryRouter(<Navigation isLoggedIn />);

    await expect(screen.getByRole("link", { name: "Community" })).toHaveAttribute("href", "https://discourse.maas.io/");
  });

  it.skip("links to the bug report page at the bottom of the nav", async () => {
    // TODO: Enable this test once a bug report link is available https://warthogs.atlassian.net/browse/MAASENG-1588
    renderWithMemoryRouter(<Navigation isLoggedIn />);

    await expect(screen.getByRole("link", { name: "Report a bug" })).toHaveAttribute("href", "");
  });

  it("removes focus from the current element after clicking the link", async () => {
    renderWithMemoryRouter(<Navigation isLoggedIn />);

    const navigationLinks = screen.getAllByRole("link");
    for (const link of navigationLinks) {
      await userEvent.click(link);
      await expect(link).not.toHaveFocus();
    }
  });

  it("displays collapsible button when user is logged out", () => {
    renderWithMemoryRouter(<Navigation isLoggedIn={false} />);

    expect(screen.getByRole("button", { name: /expand main navigation/i })).toBeInTheDocument();
  });

  it("does not display in-app navigation links when logged out", () => {
    renderWithMemoryRouter(<Navigation isLoggedIn={false} />);

    navItems.map(({ label }) =>
      expect(screen.queryByRole("link", { name: new RegExp(label, "i") })).not.toBeInTheDocument(),
    );
  });

  it("should be collapsed on user logout", async () => {
    renderWithMemoryRouter(<Navigation isLoggedIn={false} />);

    await expect(screen.getByRole("navigation")).toHaveClass("is-collapsed");
  });

  it("removes focus from the current element after clicking the link", async () => {
    renderWithMemoryRouter(<Navigation isLoggedIn />);
    const navigationLinks = screen.getAllByRole("link");
    for (const link of navigationLinks) {
      await userEvent.click(link);
      await expect(link).not.toHaveFocus();
    }
  });

  it("does not display in-app navigation links when logged out", () => {
    renderWithMemoryRouter(<Navigation isLoggedIn={false} />);

    navItems.map(({ label }) =>
      expect(screen.queryByRole("link", { name: new RegExp(label, "i") })).not.toBeInTheDocument(),
    );
  });

  it("displays external links when user is logged out", () => {
    renderWithMemoryRouter(<Navigation isLoggedIn={false} />);

    navItemsBottom.map(({ label }) =>
      expect(screen.getByRole("link", { name: new RegExp(label, "i") })).toBeInTheDocument(),
    );
  });

  it("displays the username of the logged in user", () => {
    renderWithMemoryRouter(<Navigation isLoggedIn />);

    expect(
      screen.getByRole("link", {
        name: /admin/i,
      }),
    ).toBeInTheDocument();
  });
});
