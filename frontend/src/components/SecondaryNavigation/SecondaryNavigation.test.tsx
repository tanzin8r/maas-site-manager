import SecondaryNavigation from "./SecondaryNavigation";

import { routesConfig } from "@/base/routesConfig";
import { renderWithMemoryRouter, screen } from "@/test-utils";

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
