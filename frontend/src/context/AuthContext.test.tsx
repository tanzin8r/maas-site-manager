import { protectedPages } from "@/config/routes";
import { AuthContextProvider } from "@/context";
import routes from "@/routes";
import { RouterProvider, createMemoryRouter } from "@/utils/router";
import { render, waitFor } from "@/utils/test-utils";

protectedPages.forEach(({ path }) => {
  it(`redirects user to login page from ${path}`, async () => {
    const router = createMemoryRouter(routes, { initialEntries: [path], initialIndex: 0 });
    render(
      <AuthContextProvider>
        <RouterProvider router={router} />
      </AuthContextProvider>,
    );
    await waitFor(() => expect(router.state.location.pathname).toEqual("/login"));
  });
});
