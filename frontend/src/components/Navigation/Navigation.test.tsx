/**
 * @vitest-environment happy-dom
 */

import { rest } from "msw";
import { setupServer } from "msw/node";

import Navigation, { navItemsBottom, navItems, settingsNavItems } from "./Navigation";

import { createMockCurrentUserResolver } from "@/mocks/resolvers";
import { getApiUrl } from "@/utils/test-urls";
import { renderWithMemoryRouter, screen, userEvent, waitFor } from "@/utils/test-utils";

const mockServer = setupServer(
  rest.get(getApiUrl("/users/me"), createMockCurrentUserResolver()),
  rest.get("https://maas.io/docs", (req, res, ctx) => res(ctx.status(200))),
  rest.get("https://discourse.maas.io/", (req, res, ctx) => res(ctx.status(200))),
  // have to use a splat path here since the actual URL contains a `+`, which throws type errors
  rest.get("https://bugs.launchpad.net/maas-site-manager/*", (req, res, ctx) => res(ctx.status(200))),
);

beforeAll(() => {
  vi.stubGlobal("location", { origin: "http://localhost:8000" });
  vi.stubGlobal("navigation", vi.fn());
  mockServer.listen();
});
afterEach(() => {
  mockServer.resetHandlers();
});
afterAll(() => {
  mockServer.close();
  vi.unstubAllGlobals();
});

it("displays navigation", () => {
  renderWithMemoryRouter(<Navigation isLoggedIn />);
  expect(screen.getByRole("banner", { name: "main navigation" })).toBeInTheDocument();
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
  expect(screen.getByRole("banner", { name: "main navigation" })).toHaveClass("is-collapsed");
});

it("persists collapsed state", async () => {
  const { rerender } = renderWithMemoryRouter(<Navigation isLoggedIn />);

  const primaryNavigation = screen.getByRole("banner", { name: "main navigation" });
  await userEvent.click(screen.getByRole("button", { name: "expand main navigation" }));
  expect(primaryNavigation).toHaveClass("is-pinned");

  rerender(<Navigation isLoggedIn />);

  expect(primaryNavigation).toHaveClass("is-pinned");
});

it("links to the documentation at the bottom of the nav", async () => {
  renderWithMemoryRouter(<Navigation isLoggedIn />);

  expect(screen.getByRole("link", { name: "Documentation" })).toHaveAttribute("href", "https://maas.io/docs");
});

it("links to MAAS discourse at the bottom of the nav", async () => {
  renderWithMemoryRouter(<Navigation isLoggedIn />);

  expect(screen.getByRole("link", { name: "Community" })).toHaveAttribute("href", "https://discourse.maas.io/");
});

it("links to the bug report page at the bottom of the nav", async () => {
  renderWithMemoryRouter(<Navigation isLoggedIn />);

  expect(screen.getByRole("link", { name: "Report a bug" })).toHaveAttribute(
    "href",
    "https://bugs.launchpad.net/maas-site-manager/+filebug",
  );
});

it("removes focus from the current element after clicking the link", async () => {
  renderWithMemoryRouter(<Navigation isLoggedIn />);

  const navigationLinks = screen.getAllByRole("link");
  for (const link of navigationLinks) {
    // console.log(`${link.textContent}: ${link.getAttribute("href")}`);
    await userEvent.click(link);
    expect(link).not.toHaveFocus();
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

  expect(screen.getByRole("banner", { name: "main navigation" })).toHaveClass("is-collapsed");
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

it("displays the username of the logged in user", async () => {
  renderWithMemoryRouter(<Navigation isLoggedIn />);

  await waitFor(() => {
    expect(
      screen.getByRole("link", {
        name: /admin/i,
      }),
    ).toBeInTheDocument();
  });
});
