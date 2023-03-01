import { test, expect } from "@playwright/test";

test.beforeEach(async ({ page }) => {
  await page.goto("/sites");
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
