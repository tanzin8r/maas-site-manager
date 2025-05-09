import { setupServer } from "msw/node";

import ImageSourceForm from "./ImageSourceForm";

import { AppLayoutContext } from "@/context";
import { BootSourceContext } from "@/context/BootSourceContext";
import { imageSourceResolvers, mockImageSources } from "@/testing/resolvers/imageSources";
import { render, userEvent, screen, waitFor } from "@/utils/test-utils";

const mockServer = setupServer(
  imageSourceResolvers.getImageSource.handler(),
  imageSourceResolvers.createImageSource.handler(),
  imageSourceResolvers.updateImageSource.handler(),
);

beforeAll(() => mockServer.listen());
afterEach(() => mockServer.resetHandlers());
afterAll(() => mockServer.close());

it("shows an error for invalid URLs", async () => {
  render(<ImageSourceForm type="add" />);

  const urlInput = screen.getByRole("textbox", { name: "URL" });

  await userEvent.type(urlInput, "not a valid URL");
  await userEvent.tab();

  expect(screen.getByText(/Not a valid URL/i)).toBeInTheDocument();
});

it("shows an error for invalid priority", async () => {
  render(<ImageSourceForm type="add" />);

  const priorityInput = screen.getByRole("textbox", { name: "Priority" });

  await userEvent.type(priorityInput, "not a number");
  await userEvent.tab();

  expect(screen.getByText(/priority must be a `number`/i)).toBeInTheDocument();

  await userEvent.clear(priorityInput);
  await userEvent.type(priorityInput, "1.5");
  await userEvent.tab();

  expect(screen.getByText(/priority must be a whole number/i)).toBeInTheDocument();
});

it("closes the side panel and resets selected source when 'Cancel' is clicked", async () => {
  const setSelected = vi.fn();
  const setSidebar = vi.fn();

  render(
    <AppLayoutContext.Provider value={{ sidebar: null, setSidebar, previousSidebar: null }}>
      <BootSourceContext.Provider value={{ selected: mockImageSources[0].id, setSelected }}>
        <ImageSourceForm type="edit" />
      </BootSourceContext.Provider>
    </AppLayoutContext.Provider>,
  );

  await waitFor(() => expect(screen.getByRole("button", { name: "Cancel" })).toBeInTheDocument());
  await userEvent.click(screen.getByRole("button", { name: "Cancel" }));

  await waitFor(() => expect(setSelected).toHaveBeenCalledWith(null));
  await waitFor(() => expect(setSidebar).toHaveBeenCalledWith(null));
});
