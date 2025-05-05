import RequireLogin from "./RequireLogin";

import { AuthContextProvider } from "@/context";
import * as router from "@/utils/router";
import { renderWithMemoryRouter } from "@/utils/test-utils";

it("should redirect to login page if user is not authenticated", () => {
  const navigate = vi.fn();
  vi.spyOn(router, "useNavigate").mockImplementation(() => navigate);
  renderWithMemoryRouter(
    <AuthContextProvider>
      <RequireLogin />
    </AuthContextProvider>,
    { initialEntries: ["/sites"] },
  );
  expect(navigate).toHaveBeenCalledWith({ pathname: "/login", search: "?redirectTo=%2Fsites" });
});
