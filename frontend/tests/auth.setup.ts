import { routesConfig } from "@/config/routes";
import { expect, test as setup } from "@playwright/test";
import { adminAuthFile } from "./constants";

setup("authenticate", async ({ page }) => {
  await page.goto(routesConfig.login.path);
  await page.getByRole("textbox", { name: "Email" }).type("admin@example.com");
  await page.getByRole("textbox", { name: "Password" }).type("admin");
  await page.getByRole("button", { name: "Login" }).click();
  await expect(page.getByRole("link", { name: "Log out" })).toBeVisible();
  await page.context().storageState({ path: adminAuthFile });
});
