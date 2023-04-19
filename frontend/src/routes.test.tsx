import { createMemoryRouter, RouterProvider } from "react-router-dom";

import { allResolvers } from "./mocks/resolvers";

import { routesConfig } from "@/base/routesConfig";
import routes from "@/routes";
import { render, screen, waitFor, setupServer } from "@/test-utils";

const mockServer = setupServer(...allResolvers);

describe("router", () => {
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

  Object.values(routesConfig).forEach(({ title, path }) => {
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
});
