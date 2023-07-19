import useSecondaryNavContext from "./useSecondaryNavContext";

import * as router from "@/router";
import { renderHook } from "@/test-utils";

afterAll(() => {
  vi.restoreAllMocks();
});

it("should return 'settings' context for /settings path", () => {
  vi.spyOn(router, "useLocation").mockImplementation(() => ({
    pathname: "/settings",
    search: "",
    hash: "",
    key: "",
    state: null,
  }));
  const { result } = renderHook(() => useSecondaryNavContext());
  expect(result.current).toEqual("settings");
});

it("should return 'account' context for /account path", () => {
  vi.spyOn(router, "useLocation").mockImplementation(() => ({
    pathname: "/account",
    search: "",
    hash: "",
    key: "",
    state: null,
  }));
  const { result } = renderHook(() => useSecondaryNavContext());
  expect(result.current).toEqual("account");
});

it("reverts to 'settings' context for any other path", () => {
  vi.spyOn(router, "useLocation").mockImplementation(() => ({
    pathname: "/",
    search: "",
    hash: "",
    key: "",
    state: null,
  }));
  const { result } = renderHook(() => useSecondaryNavContext());
  expect(result.current).toEqual("settings");
});
