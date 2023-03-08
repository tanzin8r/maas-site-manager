import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";

import { render, screen } from "../../test-utils";

import Navigation from "./Navigation";

describe("Navigation", () => {
  it("displays navigation", () => {
    render(
      <MemoryRouter initialEntries={[{ pathname: "/", key: "testKey" }]}>
        <Navigation />
      </MemoryRouter>,
    );
    expect(screen.getByRole("navigation")).toBeInTheDocument();
  });

  it("can highlight an active URL", () => {
    render(
      <MemoryRouter initialEntries={[{ pathname: "/sites", key: "testKey" }]}>
        <Navigation />
      </MemoryRouter>,
    );

    const currentMenuItem = screen.getAllByRole("link", { current: "page" })[0];
    expect(currentMenuItem).toBeInTheDocument();
    expect(currentMenuItem).toHaveTextContent("Overview");
  });

  it("highlights 'Overview' when active", () => {
    render(
      <MemoryRouter initialEntries={[{ pathname: "/sites", key: "testKey" }]}>
        <Navigation />
      </MemoryRouter>,
    );

    const currentMenuItem = screen.getAllByRole("link", { current: "page" })[0];
    expect(currentMenuItem).toBeInTheDocument();
    expect(currentMenuItem).toHaveTextContent("Overview");
  });

  it("highlights 'Settings' when active", () => {
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
});
