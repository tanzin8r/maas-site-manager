import SecondaryNavigation from "./SecondaryNavigation";

import { routesConfig } from "@/config/routes";
import { renderWithMemoryRouter, screen } from "@/utils/test-utils";

it("renders settings secondary navigation", async () => {
  renderWithMemoryRouter(<SecondaryNavigation />);

  expect(screen.getByRole("heading", { level: 2, name: /Settings/i })).toBeInTheDocument();
  expect(screen.getByRole("link", { name: /Tokens/i })).toBeInTheDocument();
  expect(screen.getByRole("link", { name: /Requests/i })).toBeInTheDocument();
});

it("highlights an active navigation item correctly settings secondary navigation", async () => {
  renderWithMemoryRouter(<SecondaryNavigation />, { initialEntries: [routesConfig.requests.path] });

  expect(screen.getByRole("heading", { level: 2, name: /Settings/i })).toBeInTheDocument();
  expect(screen.getByRole("link", { current: "page" })).toHaveTextContent(routesConfig.requests.title);
});

it("displays 'Account' title on account page", () => {
  renderWithMemoryRouter(<SecondaryNavigation />, { initialEntries: [routesConfig.account.path] });

  expect(screen.getByRole("heading", { level: 2, name: /account/i })).toBeInTheDocument();
});
