import { test, expect } from "@playwright/test";

import { adminAuthFile } from "./constants";
import { routesConfig } from "@/base/routesConfig";

test.use({ storageState: adminAuthFile });

test.beforeEach(async ({ page }) => {
  await page.goto(routesConfig.sites.path);
});

test("can hide table columns", async ({ page }) => {
  const columnsCount = 6;
  const columnHeaders = await page.locator("th");
  await expect(columnHeaders).toHaveCount(columnsCount);
  await expect(columnHeaders).toHaveText(["", /name/i, /connection/i, /country/i, /local time/i, /machines/i]);
  await page.getByRole("button", { name: "Columns" }).click();
  await page.getByLabel("submenu").getByRole("checkbox", { name: "connection" }).click({ force: true });

  const updatedColumnHeaders = await page.locator("th");
  expect(updatedColumnHeaders).toHaveCount(columnsCount - 1);

  await expect(columnHeaders).toHaveText(["", /name/i, /country/i, /local time/i, /machines/i]);

  await page.reload();

  // verify that the hidden column is still hidden after refresh
  const refreshedColumnHeaders = await page.locator("th");
  expect(refreshedColumnHeaders).toHaveCount(columnsCount - 1);
  await expect(refreshedColumnHeaders).toHaveText(["", /name/i, /country/i, /local time/i, /machines/i]);
});

test("opens remove regions panel if remove button is pressed", async ({ page }) => {
  await expect(page.getByRole("dialog", { name: /Remove regions/i })).not.toBeVisible();
  await page.getByRole("checkbox", { name: /select all/i }).click({ force: true });
  await page.getByRole("button", { name: /Remove/i }).click();
  await expect(page.getByRole("dialog", { name: /Remove regions/i })).toBeVisible();
});

test("can close remove regions panel using Escape key", async ({ page }) => {
  const dialog = page.getByRole("dialog", { name: /Remove regions/i });
  await expect(dialog).not.toBeVisible();
  await page.getByRole("checkbox", { name: /select all/i }).click({ force: true });
  await page.getByRole("button", { name: /Remove/i }).click();
  await expect(dialog).toBeVisible();
  await dialog.press("Escape");
  await expect(dialog).not.toBeVisible();
});
