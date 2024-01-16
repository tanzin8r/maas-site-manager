import ImagesList from "./ImagesList";

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

it("displays the images list", () => {
  renderWithMemoryRouter(<ImagesList />);

  expect(screen.getByText("Images")).toBeInTheDocument();
});

it("displays 'Delete', 'Download images', and 'Upload Image' buttons", () => {
  renderWithMemoryRouter(<ImagesList />);

  expect(screen.getByRole("button", { name: /Delete/i })).toBeInTheDocument();
  expect(screen.getByRole("button", { name: /Download images/i })).toBeInTheDocument();
  expect(screen.getByRole("button", { name: /Upload Image/i })).toBeInTheDocument();
});
