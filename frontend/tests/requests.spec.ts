import { test, expect } from "@playwright/test";
import { adminAuthFile } from "./constants";

import { routesConfig } from "@/base/routesConfig";

test.use({ storageState: adminAuthFile });

test.beforeEach(async ({ page }) => {
  await page.goto(routesConfig.requests.path);
});

test("goes to the regions page if the user clicks on the regions link", async ({ page }) => {
  await expect(page.getByRole("heading", { name: /regions/i })).toBeHidden();
  await page.getByRole("checkbox", { name: "select all" }).click({ force: true });
  await page.getByRole("button", { name: /Accept/i }).click();
  await expect(page.getByRole("alert").getByText(/Accepted enrolment request for [0-9]+ MAAS regions/i)).toBeVisible();
  await page.getByRole("button", { name: /Go to Regions/i }).click();
  await page.waitForURL(routesConfig.sitesList.path);
});
