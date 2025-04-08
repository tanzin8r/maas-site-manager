import { routesConfig } from "@/config/routes";
import { expect, test as setup } from "@playwright/test";
import { adminAuthFile } from "./constants";

setup("authenticate", async ({ page }) => {
  await page.goto(routesConfig.login.path);
  await page.getByRole("textbox", { name: "Email" }).type("admin@example.com");
  await page.getByRole("textbox", { name: "Password" }).type("admin");
  await page.getByRole("button", { name: "Login" }).click();

  // eslint-disable-next-line playwright/no-standalone-expect
  await expect(page.getByRole("link", { name: "Log out" })).toBeVisible();

  // Accept OSM ToS so that the map is enabled
  await page.goto(routesConfig.mapSettings.path);
  await page
    .getByRole("checkbox", {
      name: "I have read and accept the OpenStreetMap term of service and their fair use policy.",
    })
    .click();
  await page.getByRole("button", { name: "Save" }).click();

  await page.context().storageState({ path: adminAuthFile });
});
