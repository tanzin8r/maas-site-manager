import SitesHiddenButton from "./SitesHiddenButton";

import { render, screen, userEvent } from "@/utils/test-utils";

it("renders the site hidden button", () => {
  render(<SitesHiddenButton />);

  expect(screen.getByRole("button", { name: "show missing sites" })).toBeInTheDocument();
});

it("displays a tooltip on button hover", async () => {
  render(<SitesHiddenButton />);

  const sitesHiddenBtn = screen.getByRole("button", { name: "show missing sites" });
  await userEvent.hover(sitesHiddenBtn);
  expect(screen.getByRole("tooltip", { name: /Some MAAS sites are not shown*/i })).toBeInTheDocument();
});
