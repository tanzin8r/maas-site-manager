import { protectedRoutes, routesConfig } from "@/base/routesConfig";
import { test, expect, Page } from "@playwright/test";
import { admin } from "./constants";

export const login = async ({ page }: { page: Page }) => {
  await page.getByRole("textbox", { name: "Username" }).type(admin.username);
  await page.getByRole("textbox", { name: "Password" }).type(admin.password);
  await page.getByRole("button", { name: "Login" }).click();
};

test.afterEach(async ({ page }) => {
  await page.getByRole("link", { name: "Log out" }).click();
});

Object.keys(protectedRoutes).forEach((url) => {
  test(`user is redirected to login page when attempting to visit ${url}`, async ({ page }) => {
    await page.goto(url);
    await expect(page).toHaveURL(`${routesConfig.login.path}?redirectTo=${encodeURIComponent("/" + url)}`);
    await login({ page });
    await expect(page).toHaveURL(url);
  });
});

test("user is redirected to enrolled sites list after login", async ({ page }) => {
  await page.goto(routesConfig.login.path);
  await login({ page });
  await expect(page).toHaveURL(routesConfig.sites.path);
});

test("user is redirected to the URL they wanted to visit", async ({ page }) => {
  await page.goto(routesConfig.requests.path);
  await login({ page });
  await expect(page).toHaveURL(routesConfig.requests.path);
});
