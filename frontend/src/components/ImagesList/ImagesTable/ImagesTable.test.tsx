import { http, HttpResponse } from "msw";

import ImagesTableContainer, { ImagesTable } from "./ImagesTable";

import { imageFactory } from "@/mocks/factories";
import { imagesResolvers } from "@/testing/resolvers/images";
import { sitesResolvers } from "@/testing/resolvers/sites";
import { apiUrls } from "@/utils/test-urls";
import { renderWithMemoryRouter, screen, setupServer, waitFor, within } from "@/utils/test-utils";

const images = imageFactory.buildList(2, { os: "Hannah Montana Linux" });
const mockServer = setupServer(imagesResolvers.listImages.handler(images), sitesResolvers.listSites.handler());

beforeAll(() => {
  mockServer.listen();
});

afterEach(() => {
  mockServer.resetHandlers();
});

afterAll(() => {
  mockServer.close();
});

it("displays images table", () => {
  renderWithMemoryRouter(<ImagesTableContainer />);
  expect(screen.getByRole("table", { name: /images/ })).toBeInTheDocument();
});

it("displays loading state", () => {
  vi.mock("@tanstack/react-query", async () => {
    const actual = await vi.importActual("@tanstack/react-query");
    return {
      ...actual,
      useQuery: vi.fn().mockReturnValue({
        data: null,
        error: null,
        isPending: true,
        isFetched: false,
      }),
    };
  });
  renderWithMemoryRouter(<ImagesTableContainer />);
  expect(within(screen.getByRole("table", { name: /images/ })).getByText(/Loading/)).toBeInTheDocument();
});

it("displays empty state if no images are available", async () => {
  mockServer.use(imagesResolvers.listImages.handler([]));
  renderWithMemoryRouter(<ImagesTableContainer />);
  await waitFor(() => expect(screen.getByText("No images")).toBeInTheDocument());
});

it("can display error message", async () => {
  mockServer.use(
    http.get(apiUrls.images, () => {
      return new HttpResponse(null, { status: 400, statusText: "error" });
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
  expect(rows[0].textContent).toContain(images[0].os);

  images.forEach((image, i) => {
    expect(rows[i + 1].textContent).toContain(image.release);
  });
});
