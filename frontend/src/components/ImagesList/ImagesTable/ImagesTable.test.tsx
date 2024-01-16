import ImagesTable from "./ImagesTable";

import { imageFactory } from "@/mocks/factories";
import { createMockImagesResolver } from "@/mocks/resolvers";
import { createMockGetServer } from "@/mocks/server";
import { apiUrls } from "@/utils/test-urls";
import { renderWithMemoryRouter, screen } from "@/utils/test-utils";

const images = imageFactory.buildList(2);
const mockServer = createMockGetServer(apiUrls.images, createMockImagesResolver(images));

beforeAll(() => {
  mockServer.listen();
});

afterEach(() => {
  mockServer.resetHandlers();
  localStorage.clear();
});

afterAll(() => {
  mockServer.close();
});

it("displays images table", () => {
  renderWithMemoryRouter(<ImagesTable />);
  expect(screen.getByRole("table", { name: /images/ })).toBeInTheDocument();
});
