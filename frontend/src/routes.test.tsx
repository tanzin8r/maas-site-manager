import { allResolvers } from "./mocks/resolvers";

import { pages } from "@/base/routesConfig";
import { createMemoryRouter, RouterProvider } from "@/router";
import routes from "@/routes";
import { render, screen, waitFor, setupServer } from "@/test-utils";

const mockServer = setupServer(...allResolvers);

beforeAll(() => {
  mockServer.listen();
  localStorage.setItem("jwtToken", "test");
});
afterEach(() => {
  mockServer.resetHandlers();
});
afterAll(() => {
  mockServer.close();
  localStorage.removeItem("jwtToken");
});

it("redirects to the default route", async () => {
  const router = createMemoryRouter(routes);
  render(<RouterProvider router={router} />);

  expect(router.state.location.pathname).toEqual("/");
  await waitFor(() => expect(router.state.location.pathname).toEqual("/sites"));
});

pages.forEach(({ title, path }) => {
  it(`displays correct document title for ${title} page`, async () => {
    const router = createMemoryRouter(routes, { initialEntries: [path], initialIndex: 0 });
    render(<RouterProvider router={router} />);
    expect(document.title).toBe(`${title} | MAAS Site Manager`);
  });
  it(`displays correct heading for ${title} page`, async () => {
    const router = createMemoryRouter(routes, { initialEntries: [path], initialIndex: 0 });
    render(<RouterProvider router={router} />);
    expect(screen.getByRole("heading", { level: 1, name: `${title} | MAAS Site Manager` })).toBeInTheDocument();
  });
});
