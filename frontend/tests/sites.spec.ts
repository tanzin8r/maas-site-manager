import { test, expect } from "@playwright/test";

import { adminAuthFile } from "./constants";
import { routesConfig } from "@/config/routes";

test.use({ storageState: adminAuthFile });

test.beforeEach(async ({ page }) => {
  await page.goto(routesConfig.sites.path);
});

test("can hide table columns", async ({ page }) => {
  const columnsCount = 8;
  const columnHeaders = page.locator("th");
  await expect(columnHeaders).toHaveCount(columnsCount);
  await expect(columnHeaders).toHaveText([
    "",
    /name/i,
    /connection/i,
    /country/i,
    /local time/i,
    /machines/i,
    /aggregated status/i,
    /columns/i,
  ]);
  await page.getByRole("button", { name: "Columns" }).click();
  await page.getByLabel("submenu").getByRole("checkbox", { name: "connection" }).click({ force: true });

  const updatedColumnHeaders = page.locator("th");
  await expect(updatedColumnHeaders).toHaveCount(columnsCount - 1);

  await expect(columnHeaders).toHaveText([
    "",
    /name/i,
    /country/i,
    /local time/i,
    /machines/i,
    /aggregated status/i,
    /columns/i,
  ]);

  await page.reload();

  // verify that the hidden column is still hidden after refresh
  const refreshedColumnHeaders = page.locator("th");
  await expect(refreshedColumnHeaders).toHaveCount(columnsCount - 1);
  await expect(refreshedColumnHeaders).toHaveText([
    "",
    /name/i,
    /country/i,
    /local time/i,
    /machines/i,
    /aggregated status/i,
    /columns/i,
  ]);
});

test("opens remove sites panel if remove button is pressed", async ({ page }) => {
  await expect(page.getByRole("complementary", { name: /Remove sites/i })).toBeHidden();
  await page.getByRole("checkbox", { name: /select all/i }).click({ force: true });
  await page.getByRole("button", { name: /Remove/i }).click();
  await expect(page.getByRole("complementary", { name: /Remove sites/i })).toBeVisible();
});

test("can close remove site panel using Escape key", async ({ page }) => {
  const dialog = page.getByRole("complementary", { name: /Remove sites/i });
  await expect(dialog).toBeHidden();
  await page.getByRole("checkbox", { name: /select all/i }).click({ force: true });
  await page.getByRole("button", { name: /Remove/i }).click();
  await expect(dialog).toBeVisible();
  await dialog.press("Escape");
  await expect(dialog).toBeHidden();
});

test("hides columns dropdown in the map view", async ({ page }) => {
  const searchAndFilter = page.getByRole("searchbox", { name: /Search and filter/i });
  const columnsDropdown = page.getByRole("button", { name: /Columns/i });
  const controlsHeading = page.getByRole("heading", { level: 2, name: /MAAS sites/i });

  await expect(searchAndFilter).toBeVisible();
  await expect(columnsDropdown).toBeVisible();
  await expect(controlsHeading).toBeVisible();

  await page.goto(routesConfig.sitesMap.path);

  await expect(searchAndFilter).toBeVisible();
  await expect(controlsHeading).toBeVisible();
  await expect(columnsDropdown).toBeHidden();
});

test("search text persists when switching pages", async ({ page }) => {
  const searchAndFilter = page.getByRole("searchbox", { name: /Search and filter/i });
  const searchText = "test";
  await searchAndFilter.fill(searchText);

  await page.waitForURL(`**/list?q=${searchText}`);
  await page.getByRole("tab", { name: /map/i }).click();
  await page.waitForURL(`**/sites/map?q=${searchText}`);
  await expect(page).toHaveURL(`http://localhost:${process.env.VITE_UI_PORT}/sites/map?q=${searchText}`);
  await expect(page.getByRole("searchbox", { name: /Search and filter/i })).toHaveValue(searchText);
  await expect(page.getByRole("tab", { name: /table/i })).toHaveAttribute("href", `/sites/list?q=${searchText}`);
});
