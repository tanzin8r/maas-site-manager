import { fakeBootSources } from "../ImageSourceList/ImageSourceList";

import DeleteImageSource from "./DeleteImageSource";

import { BootSourceContext } from "@/context/BootSourceContext";
import { render, screen } from "@/utils/test-utils";

const renderForm = async (id: number) => {
  const view = render(
    <BootSourceContext.Provider value={{ selected: id, setSelected: vi.fn() }}>
      <DeleteImageSource />
    </BootSourceContext.Provider>,
  );
  return view;
};

it("shows the name of the site in the title and description", () => {
  renderForm(fakeBootSources.items[1].id);

  expect(screen.getByRole("heading", { name: `Remove ${fakeBootSources.items[1].url}?` })).toBeInTheDocument();
  expect(
    screen.getByText(
      `Are you sure you want to remove ${fakeBootSources.items[1].url} as an image source in MAAS Site Manager?`,
    ),
  );
});
