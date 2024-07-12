import { rest } from "msw";

import ImagesTableContainer, { ImagesTable } from "./ImagesTable";

import { imageFactory } from "@/mocks/factories";
import { createMockImagesResolver } from "@/mocks/resolvers";
import { apiUrls } from "@/utils/test-urls";
import { renderWithMemoryRouter, screen, setupServer, waitFor, within } from "@/utils/test-utils";

const images = imageFactory.buildList(2, { name: "Hannah Montana Linux" });
const initialHandlers = [rest.get(apiUrls.images, createMockImagesResolver(images))] as const;
const mockServer = setupServer(...initialHandlers);

beforeAll(() => {
  mockServer.listen();
});

afterEach(() => {
  mockServer.resetHandlers(...initialHandlers);
});

afterAll(() => {
  mockServer.close();
});

it("displays images table", () => {
  renderWithMemoryRouter(<ImagesTableContainer />);
  expect(screen.getByRole("table", { name: /images/ })).toBeInTheDocument();
});

it("displays loading state", () => {
  mockServer.resetHandlers(
    rest.get(apiUrls.images, (req, res, ctx) => {
      return res(ctx.delay(Infinity));
    }),
  );
  renderWithMemoryRouter(<ImagesTableContainer />);
  expect(within(screen.getByRole("table", { name: /images/ })).getByText(/Loading/)).toBeInTheDocument();
});

it("displays empty state if no images are available", async () => {
  mockServer.resetHandlers(rest.get(apiUrls.images, createMockImagesResolver([])));
  renderWithMemoryRouter(<ImagesTableContainer />);
  await waitFor(() => expect(screen.getByText("No images")).toBeInTheDocument());
});

it("can display error message", async () => {
  mockServer.resetHandlers(
    rest.get(apiUrls.images, (req, res, ctx) => {
      return res(ctx.status(400, "error"));
    }),
  );
  renderWithMemoryRouter(
    <ImagesTable
      error={new Error("custom error")}
      isPending={false}
      rowSelection={{}}
      setRowSelection={vi.fn(() => {})}
      setSidebar={vi.fn(() => {})}
      setSorting={vi.fn(() => [])}
      sorting={[]}
    />,
  );
  await waitFor(() => expect(screen.getByText("custom error")).toBeInTheDocument());
});

it("can display images", async () => {
  renderWithMemoryRouter(<ImagesTableContainer />);

  await waitFor(() => {
    const table = screen.getByRole("table", { name: /images/ });
    expect(within(table).queryByText(/Loading/)).not.toBeInTheDocument();
  });

  const tableBody = screen.getAllByRole("rowgroup")[1];

  const rows = within(tableBody).getAllByRole("row");

  expect(rows[0].textContent).toContain(images[0].name);

  images.forEach((image, i) => {
    expect(rows[i + 1].textContent).toContain(image.release);
  });
});
