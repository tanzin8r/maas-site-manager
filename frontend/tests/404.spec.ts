import { test, expect } from "@playwright/test";
import { adminAuthFile } from "./constants";

test.use({ storageState: adminAuthFile });

test("displays a 404 page correctly for nested routes", async ({ page }) => {
  await page.goto("/no-such-page");
  await expect(page).toHaveTitle(/MAAS Site Manager/);
  await expect(page.getByText(/404: Page not found/)).toBeVisible();
  await expect(page.getByText("Can't find page for: /no-such-page")).toBeVisible();
});
