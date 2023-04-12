import * as reactRouter from "react-router";
import { vi } from "vitest";

import RequireLogin from "./RequireLogin";

import api from "@/api";
import { AuthContextProvider } from "@/context";
import { renderWithMemoryRouter } from "@/test-utils";

it("should redirect to login page if user is not authenticated", () => {
  const navigate = vi.fn();
  vi.spyOn(reactRouter, "useNavigate").mockImplementation(() => navigate);
  renderWithMemoryRouter(
    <AuthContextProvider apiClient={api}>
      <RequireLogin />
    </AuthContextProvider>,
    { initialEntries: ["/sites"] },
  );
  expect(navigate).toHaveBeenCalledWith({ pathname: "/login", search: "?redirectTo=%2Fsites" });
});
