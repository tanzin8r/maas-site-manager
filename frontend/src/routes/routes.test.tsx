import { pages } from "@/config/routes";
import { allResolvers } from "@/mocks/resolvers";
import routes from "@/routes";
import { createMemoryRouter, RouterProvider } from "@/utils/router";
import { render, screen, waitFor, setupServer } from "@/utils/test-utils";

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
  await waitFor(() => expect(router.state.location.pathname).toEqual("/sites/list"));
});

pages.forEach(({ title, path }) => {
  it(`displays a correct page for ${path} route`, async () => {
    const router = createMemoryRouter(routes, { initialEntries: [path], initialIndex: 0 });
    render(<RouterProvider router={router} />);
    await waitFor(() => expect(router.state.location.pathname).toEqual(path));
  });
  it(`displays correct document title and heading for ${title} page`, async () => {
    const router = createMemoryRouter(routes, { initialEntries: [path], initialIndex: 0 });
    render(<RouterProvider router={router} />);
    await waitFor(() => expect(document.title).toBe(`${title} | MAAS Site Manager`));
    expect(screen.getByRole("heading", { level: 1, name: `${title} | MAAS Site Manager` })).toBeInTheDocument();
  });
});
