import NavigationBanner from "./NavigationBanner";

import { BrowserRouter } from "@/router";
import { screen, render } from "@/test-utils";

it("displays a link to the homepage", () => {
  render(
    <BrowserRouter>
      <NavigationBanner />
    </BrowserRouter>,
  );

  expect(screen.getByRole("link", { name: /Homepage/ })).toBeInTheDocument();
});
