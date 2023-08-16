import { test, expect } from "@playwright/test";
import { adminAuthFile } from "./constants";

import { routesConfig } from "@/config/routes";

test.use({ storageState: adminAuthFile });

test.beforeEach(async ({ page }) => {
  await page.goto(routesConfig.requests.path);
});

test("goes to the sites page if the user clicks on the sites link", async ({ page }) => {
  await expect(page.getByRole("heading", { name: /sites/i })).toBeHidden();
  await page.getByRole("checkbox", { name: "select all" }).click({ force: true });
  await page.getByRole("button", { name: /Accept/i }).click();
  await expect(page.getByRole("alert").getByText(/Accepted enrolment request for [0-9]+ MAAS sites/i)).toBeVisible();
  await page.getByRole("button", { name: /Go to Sites/i }).click();
  await page.waitForURL(routesConfig.sitesList.path);
});
