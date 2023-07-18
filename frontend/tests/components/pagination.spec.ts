import { test, expect } from "@playwright/test";

import { adminAuthFile } from "../constants";
import { routesConfig } from "@/base/routesConfig";

test.use({ storageState: adminAuthFile });

const pagesWithPagination = [routesConfig.tokens, routesConfig.requests];

for (const pageWithTable of pagesWithPagination) {
  test.describe("navigates to the correct page on user input", () => {
    test(`${pageWithTable.title} page`, async ({ page }) => {
      await page.goto(pageWithTable.path);

      const currentPage = page.getByRole("spinbutton", { name: /current page/i });
      const nextPage = page.getByRole("button", { name: /next page/i });
      const previousPage = page.getByRole("button", { name: /previous page/i });

      await expect(currentPage).toHaveValue("1");
      await nextPage.click();
      await nextPage.click();
      await expect(currentPage).toHaveValue("3");
      await previousPage.click();
      await expect(currentPage).toHaveValue("2");
      await currentPage.fill("1");
      await expect(currentPage).toHaveValue("1");
    });
  });
}
