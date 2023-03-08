import { BrowserRouter } from "react-router-dom";

import { screen, render } from "../../../test-utils";

import NavigationBanner from "./NavigationBanner";

describe("Navigation Banner", () => {
  it("displays a link to the homepage", () => {
    render(
      <BrowserRouter>
        <NavigationBanner />
      </BrowserRouter>,
    );

    expect(screen.getByRole("link", { name: /Homepage/ })).toBeInTheDocument();
  });
});
