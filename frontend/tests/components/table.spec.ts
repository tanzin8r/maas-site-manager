import { test, expect } from "@playwright/test";

import { adminAuthFile } from "../constants";
import { routesConfig } from "@/base/routesConfig";

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
    const selectAll = await page.getByRole("checkbox", { name: /select all/i });
    const tableBodyCheckboxes = await page.locator("tbody").getByRole("checkbox").all();
    // click a single item on the first page
    await await page.locator("tbody").getByRole("checkbox").first().click({ force: true });
    await page.getByRole("button", { name: "next page" }).click();
    await expect(selectAll).toHaveAttribute("aria-checked", "mixed");
    // click partially checked select all checkbox on the second page
    await selectAll.click({ force: true });
    await expect(selectAll).toBeChecked();
    await expect(selectAll).not.toHaveAttribute("aria-checked", "mixed");
    for await (const checkbox of tableBodyCheckboxes) {
      await expect(checkbox).toBeChecked();
    }
    await page.getByRole("button", { name: "next page" }).click();
    for await (const checkbox of tableBodyCheckboxes) {
      await expect(checkbox).not.toBeChecked();
    }
  });

  test(`${pageWithTable.title} - clicking checked select all checkbox deselects items on all pages`, async ({
    page,
  }) => {
    await page.goto(pageWithTable.path);
    const selectAll = await page.getByRole("checkbox", { name: /select all/i });
    const tableBodyCheckboxes = await page.locator("tbody").getByRole("checkbox").all();
    // select all items on the first page
    await selectAll.click({ force: true });
    await page.getByRole("button", { name: "next page" }).click();
    await expect(selectAll).toHaveAttribute("aria-checked", "mixed");
    // select all items on the second page
    await selectAll.click({ force: true });
    await expect(selectAll).toBeChecked();
    // click selected 'select all' checkbox on the second page
    await selectAll.click({ force: true });
    for await (const checkbox of tableBodyCheckboxes) {
      await expect(checkbox).not.toBeChecked();
    }
    await page.getByRole("button", { name: "previous page" }).click();
    for await (const checkbox of tableBodyCheckboxes) {
      await expect(checkbox).not.toBeChecked();
    }
  });
}
