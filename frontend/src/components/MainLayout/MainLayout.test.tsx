import { setupServer } from "msw/node";

import MainLayout from "./MainLayout";

import { allResolvers } from "@/mocks/resolvers";
import { renderWithMemoryRouter, screen, waitFor } from "@/test-utils";

const mockServer = setupServer(...allResolvers);

beforeAll(() => {
  mockServer.listen();
});
afterAll(() => {
  mockServer.close();
});

it("renders header", async () => {
  renderWithMemoryRouter(<MainLayout />);

  await waitFor(() =>
    expect(screen.getByRole("heading", { level: 1, name: /MAAS Site Manager/i })).toBeInTheDocument(),
  );
});
