import { test, expect } from "@playwright/test";

import { LONG_EXPECTATION_TIMEOUT, LONG_TEST_TIMEOUT, adminAuthFile } from "./constants";
import { routesConfig } from "@/config/routes";

test.use({ storageState: adminAuthFile });

test.beforeEach(async ({ page }) => {
  test.setTimeout(LONG_TEST_TIMEOUT);
  await page.emulateMedia({ reducedMotion: "reduce" });
  await page.goto(routesConfig.sitesMap.path);
  const map = page.getByRole("region", { name: "sites map" });

  // eslint-disable-next-line playwright/no-standalone-expect
  await expect(map).toBeVisible({ timeout: LONG_EXPECTATION_TIMEOUT });
});

test("displays site markers", async ({ page }) => {
  const map = page.getByRole("region", { name: "sites map" });
  await expect(map.getByRole("button", { name: /site location marker/i }).first()).toBeVisible();
  // opens site edit on click of a marker
  const editSite = page.getByRole("complementary", { name: /Site details/i });
  await expect(editSite).not.toBeAttached();
  // displays site details after pressing a marker
  await page
    .getByRole("button", { name: /site location marker/i })
    .first()
    .press("Enter");
  await expect(editSite).toBeVisible();
});

test("returns to previous side panel if it exists", async ({ page }) => {
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
