import { test, expect, Page } from "@playwright/test";
import { admin, LONG_TEST_TIMEOUT } from "./constants";
import { routesConfig } from "@/config/routes";
import { scenarios } from "@/mocks/scenarios";

test.setTimeout(LONG_TEST_TIMEOUT);

export const login = async ({ page }: { page: Page }) => {
  await page.getByRole("textbox", { name: "Email" }).type(admin.email);
  await page.getByRole("textbox", { name: "Password" }).type(admin.password);
  await page.getByRole("button", { name: "Login" }).click();
};

test("redirects unauthenticated user to login page when attempting to visit sites list", async ({ page }) => {
  const protectedRoute = routesConfig.sitesList.path;

  await page.goto(protectedRoute);
  const expectedURL = `${routesConfig.login.path}?redirectTo=${encodeURIComponent(protectedRoute)}`;
  await page.waitForURL(/\/login/, { timeout: LONG_TEST_TIMEOUT });
  await expect(page).toHaveURL(expectedURL, { timeout: LONG_TEST_TIMEOUT });
});

test("user is redirected to enrolled sites list after login", async ({ page }) => {
  await page.goto(routesConfig.login.path);
  await login({ page });
  await expect(page).toHaveURL(routesConfig.sitesList.path);
});

test("user is redirected to the URL they wanted to visit", async ({ page }) => {
  await page.goto(routesConfig.requests.path);
  await login({ page });
  await expect(page).toHaveURL(routesConfig.requests.path);
});

test("maintains authentication state after page reload", async ({ page }) => {
  await page.goto(routesConfig.sitesList.path);
  await login({ page });
  await expect(page).toHaveURL(routesConfig.sitesList.path);
  await page.reload();
  await expect(page).toHaveURL(routesConfig.sitesList.path);
});

test("redirects to login page when API returns 401", async ({ page }) => {
  await page.goto(routesConfig.login.path);
  await login({ page });
  const protectedRoute = routesConfig.sitesList.path;
  await page.goto(`${protectedRoute}?scenario=${scenarios.sitesUnauthorized}`);
  await page.waitForURL(/\/login/, { timeout: LONG_TEST_TIMEOUT });
  await expect(page).toHaveURL(`${routesConfig.login.path}?redirectTo=${encodeURIComponent(protectedRoute)}`);
});
