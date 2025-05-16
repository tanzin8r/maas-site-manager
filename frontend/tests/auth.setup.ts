import { routesConfig } from "@/config/routes";
import { expect, test as setup } from "@playwright/test";
import { adminAuthFile, LONG_EXPECTATION_TIMEOUT, LONG_TEST_TIMEOUT } from "./constants";
import fs from "fs";
import path from "path";

setup.setTimeout(LONG_TEST_TIMEOUT);

setup("authenticate", async ({ page }) => {
  const authDir = path.dirname(adminAuthFile);
  if (!fs.existsSync(authDir)) {
    fs.mkdirSync(authDir, { recursive: true });
  }

  await page.goto(routesConfig.login.path);

  // eslint-disable-next-line playwright/no-networkidle
  await page.waitForLoadState("networkidle");

  const emailInput = page.getByRole("textbox", { name: "Email" });
  await emailInput.waitFor({ state: "visible", timeout: LONG_EXPECTATION_TIMEOUT });

  await emailInput.type("admin@example.com");
  await page.getByRole("textbox", { name: "Password" }).type("admin");

  await page.getByRole("button", { name: "Login" }).click();

  // eslint-disable-next-line playwright/no-standalone-expect
  await expect(page.getByRole("link", { name: "Log out" })).toBeVisible({ timeout: LONG_EXPECTATION_TIMEOUT });
  await page.goto(routesConfig.mapSettings.path);

  await page
    .getByRole("checkbox", {
      name: "I have read and accept the OpenStreetMap term of service and their fair use policy.",
    })
    .waitFor({ state: "visible", timeout: LONG_EXPECTATION_TIMEOUT });

  await page
    .getByRole("checkbox", {
      name: "I have read and accept the OpenStreetMap term of service and their fair use policy.",
    })
    .click();

  await page.getByRole("button", { name: "Save" }).click();
  await page.context().storageState({ path: adminAuthFile });
});
