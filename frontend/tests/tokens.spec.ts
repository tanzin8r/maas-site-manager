import { test, expect } from "@playwright/test";

import { adminAuthFile } from "./constants";
import { routesConfig } from "@/config/routes";

test.use({ storageState: adminAuthFile });

test.beforeEach(async ({ page }) => {
  await page.goto(routesConfig.tokens.path);
});

test("can open and close token generate form", async ({ page }) => {
  await page.getByRole("button", { name: /Generate tokens/i }).click();
  await expect(page.getByRole("form", { name: /Generate new enrolment tokens/i })).toBeVisible();
  await page.getByRole("button", { name: /Cancel/i }).click();
  await expect(page.getByRole("form", { name: /Generate new enrolment tokens/i })).toBeHidden();
});

test("can close token generate dialog using Escape key", async ({ page }) => {
  await page.getByRole("button", { name: /Generate tokens/i }).click();
  const dialog = page.getByRole("complementary", { name: /generate tokens/i });
  await expect(dialog).toBeVisible();
  await dialog.press("Escape");
  await expect(dialog).toBeHidden();
});

test("token create form is closed when navigating away", async ({ page }) => {
  await page.getByRole("button", { name: /Generate tokens/i }).click();
  await expect(page.getByRole("form", { name: /Generate new enrolment tokens/i })).toBeVisible();

  const mobileBanner = await page.getByRole("banner", { name: /navigation/i }).isVisible();
  // eslint-disable-next-line playwright/no-conditional-in-test
  if (mobileBanner) {
    await page
      .getByRole("banner", { name: /navigation/ })
      .getByRole("button", { name: /menu/i })
      .click();
  } else {
    await page.getByRole("navigation", { name: /main/i }).hover();
  }
  await page.getByRole("navigation", { name: /main/i }).getByRole("link", { name: /Sites/ }).click();

  await page.goBack();
  await expect(page.getByRole("form", { name: /Generate new enrolment tokens/i })).toBeHidden();
});

test("closes and clears the form after creating the token", async ({ page }) => {
  await page.getByRole("button", { name: /Generate tokens/i }).click();
  await page.getByRole("textbox", { name: /Amount of tokens to generate/i }).type("1");
  await page.getByRole("textbox", { name: /Expiration time/i }).type("1 week");
  await page
    .getByRole("form", { name: /Generate new enrolment tokens/i })
    .getByRole("button", { name: /Generate tokens/i })
    .click();
  await page.waitForResponse((resp) => resp.url().includes("/tokens") && resp.status() === 200);
  await expect(page.getByRole("form", { name: /Generate new enrolment tokens/i })).toBeHidden();
  // check that the form has been reset
  await page.getByRole("button", { name: /Generate tokens/i }).click();
  await expect(
    page
      .getByRole("form", { name: /Generate new enrolment tokens/i })
      .getByRole("button", { name: /Generate tokens/i }),
  ).toBeDisabled();
});
