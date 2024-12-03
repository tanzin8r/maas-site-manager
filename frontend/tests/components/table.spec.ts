import { test, expect } from "@playwright/test";

import { adminAuthFile } from "../constants";
import { routesConfig } from "@/config/routes";

test.use({ storageState: adminAuthFile });

const pagesWithTable = [routesConfig.tokens, routesConfig.requests, routesConfig.sites];

for (const pageWithTable of pagesWithTable) {
  test(`${pageWithTable.title} - clicking unchecked 'select all' checkbox selects all items on the current page`, async ({
    page,
  }) => {
    await page.goto(pageWithTable.path);
    await page.getByRole("checkbox", { name: /select all/i }).click({ force: true });
    const tableBodyCheckboxes = await page.locator("tbody").getByRole("checkbox").all();
    for await (const checkbox of tableBodyCheckboxes) {
      await expect(checkbox).toBeChecked();
    }
    await page.getByRole("checkbox", { name: /select all/i }).click({ force: true });
    for await (const checkbox of tableBodyCheckboxes) {
      await expect(checkbox).not.toBeChecked();
    }
  });

  test(`${pageWithTable.title} - clicking partially checked 'select all' checkbox selects all items on the current page`, async ({
    page,
  }) => {
    await page.goto(pageWithTable.path);
    const selectAll = page.getByRole("checkbox", { name: /select all/i });
    const tableBodyCheckboxes = await page.locator("tbody").getByRole("checkbox").all();
    // click a single item
    await page.locator("tbody").getByRole("checkbox").first().click({ force: true });
    await expect(selectAll).toHaveAttribute("aria-checked", "mixed");
    // click partially checked select all checkbox
    await selectAll.click({ force: true });
    await expect(selectAll).toBeChecked();
    await expect(selectAll).not.toHaveAttribute("aria-checked", "mixed");
    for await (const checkbox of tableBodyCheckboxes) {
      await expect(checkbox).toBeChecked();
    }
  });

  test(`${pageWithTable.title} - clicking checked select all checkbox deselects items`, async ({ page }) => {
    await page.goto(pageWithTable.path);
    const selectAll = page.getByRole("checkbox", { name: /select all/i });
    const tableBodyCheckboxes = await page.locator("tbody").getByRole("checkbox").all();
    // select all items on the first page
    await selectAll.click({ force: true });
    await expect(selectAll).toBeChecked();
    // click selected 'select all' checkbox
    await selectAll.click({ force: true });
    for await (const checkbox of tableBodyCheckboxes) {
      await expect(checkbox).not.toBeChecked();
    }
  });

  test(`${pageWithTable.title} - changing page deselects all items`, async ({ page }) => {
    await page.goto(pageWithTable.path);
    const selectAll = page.getByRole("checkbox", { name: /select all/i });
    const tableBodyCheckboxes = await page.locator("tbody").getByRole("checkbox").all();
    // select all items on the first page
    await selectAll.click({ force: true });
    await expect(selectAll).toBeChecked();
    for await (const checkbox of tableBodyCheckboxes) {
      await expect(checkbox).toBeChecked();
    }
    // go to the next page
    await page.getByRole("button", { name: /next page/i }).click();
    await expect(selectAll).not.toBeChecked();
    for await (const checkbox of tableBodyCheckboxes) {
      await expect(checkbox).not.toBeChecked();
    }

    // go back to the previous page
    await page.getByRole("button", { name: /previous page/i }).click();
    await expect(selectAll).not.toBeChecked();
    for await (const checkbox of tableBodyCheckboxes) {
      await expect(checkbox).not.toBeChecked();
    }
  });

  test(`${pageWithTable.title} - changing page size deselects all items`, async ({ page }) => {
    await page.goto(pageWithTable.path);
    const selectAll = page.getByRole("checkbox", { name: /select all/i });
    const tableBodyCheckboxes = await page.locator("tbody").getByRole("checkbox").all();
    // select all items on the first page
    await selectAll.click({ force: true });
    await expect(selectAll).toBeChecked();
    for await (const checkbox of tableBodyCheckboxes) {
      await expect(checkbox).toBeChecked();
    }
    // change page size
    await page.getByRole("combobox", { name: /items per page/i }).selectOption({ label: "30/page" });
    await expect(selectAll).not.toBeChecked();
    for await (const checkbox of tableBodyCheckboxes) {
      await expect(checkbox).not.toBeChecked();
    }
  });
}
