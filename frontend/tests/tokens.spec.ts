import { test, expect } from "@playwright/test";

test.beforeEach(async ({ page }) => {
  await page.goto("/tokens");
});

test("can open and close token generate form", async ({ page }) => {
  await page.getByRole("button", { name: /Generate tokens/i }).click();
  expect(page.getByRole("form", { name: /Generate new enrollment tokens/i })).toBeVisible();
  await page.getByRole("button", { name: /Cancel/i }).click();
  await expect(page.getByRole("form", { name: /Generate new enrollment tokens/i })).toBeHidden();
});

test("token create form persists its open state when navigating back", async ({ page }) => {
  await page.getByRole("button", { name: /Generate tokens/i }).click();
  await expect(page.getByRole("form", { name: /Generate new enrollment tokens/i })).toBeVisible();

  const mobileBanner = await page.getByRole("banner", { name: /navigation/i }).isVisible();
  if (mobileBanner) {
    await page
      .getByRole("banner", { name: /navigation/ })
      .getByRole("button", { name: /menu/i })
      .click();
  } else {
    await page.getByRole("navigation", { name: /main/i }).hover();
  }
  await page
    .getByRole("navigation", { name: /main/i })
    .getByRole("link", { name: /Overview/ })
    .click();

  await page.goBack();
  await expect(page.getByRole("form", { name: /Generate new enrollment tokens/i })).toBeVisible();
});

test("closes and clears the form after creating the token", async ({ page }) => {
  await page.getByRole("button", { name: /Generate tokens/i }).click();
  await page.getByRole("textbox", { name: /Amount of tokens to generate/i }).type("1");
  await page.getByRole("textbox", { name: /Expiration time/i }).type("1 week");
  await page
    .getByRole("form", { name: /Generate new enrollment tokens/i })
    .getByRole("button", { name: /Generate tokens/i })
    .click();
  await page.waitForResponse((resp) => resp.url().includes("/tokens") && resp.status() === 200);
  await expect(page.getByRole("form", { name: /Generate new enrollment tokens/i })).toBeHidden();
  // check that the form has been reset
  await page.getByRole("button", { name: /Generate tokens/i }).click();
  await expect(
    page
      .getByRole("form", { name: /Generate new enrollment tokens/i })
      .getByRole("button", { name: /Generate tokens/i }),
  ).toBeDisabled();
});
