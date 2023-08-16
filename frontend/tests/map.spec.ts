import { test, expect } from "@playwright/test";

import { adminAuthFile } from "./constants";
import { routesConfig } from "@/config/routes";

test.use({ storageState: adminAuthFile });

test.beforeEach(async ({ page }) => {
  await page.goto(routesConfig.sitesMap.path);
});

test("displays site markers", async ({ page }) => {
  const map = page.getByRole("region", { name: "sites map" });
  // displays markers
  await expect(map).toBeVisible({ timeout: 5000 });
  await expect(map.getByRole("button", { name: /site location marker/i }).first()).toBeVisible();
  // opens site edit on click of a marker
  const editSite = page.getByRole("complementary", { name: /Site details/i });
  await expect(editSite).not.toBeAttached();
  await page
    .getByRole("button", { name: /site location marker/i })
    .first()
    .press("Enter");
  await expect(editSite).toBeVisible();
});

test("returns to previous side panel if it exists", async ({ page }) => {
  const map = page.getByRole("region", { name: "sites map" });
  await expect(map).toBeVisible({ timeout: 5000 });
  await page
    .getByRole("button", { name: /site location marker/i })
    .first()
    .press("Enter");
  await page
    .getByRole("complementary", { name: /Site details/i })
    .getByRole("button", { name: "Edit" })
    .click();

  await expect(page.getByRole("complementary", { name: /Edit site/i })).toBeVisible();

  await page.getByRole("button", { name: /Cancel/i }).click();

  await expect(page.getByRole("complementary", { name: /Site details/i })).toBeVisible();
});
