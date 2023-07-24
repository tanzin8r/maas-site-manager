import NavigationBanner from "./NavigationBanner";

import { BrowserRouter } from "@/utils/router";
import { screen, render } from "@/utils/test-utils";

it("displays a link to the homepage", () => {
  render(
    <BrowserRouter>
      <NavigationBanner />
    </BrowserRouter>,
  );

  expect(screen.getByRole("link", { name: /Homepage/ })).toBeInTheDocument();
});
