import { expect, test } from "@playwright/test";

import { routesConfig } from "@/app/base/routes";
import fs from "fs";
import { adminAuthFile } from "./constants";
test.use({ storageState: adminAuthFile });

test.beforeEach(async ({ page }) => {
  await page.goto(routesConfig.tokens.path);
});

test("can open and close token generate form", async ({ page }) => {
  await page.getByRole("button", { name: /Generate tokens/i }).click();
  await expect(page.getByRole("form", { name: /Generate new enrollment tokens/i })).toBeVisible();
  await page.getByRole("button", { name: /Cancel/i }).click();
  await expect(page.getByRole("form", { name: /Generate new enrollment tokens/i })).toBeHidden();
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
  await expect(page.getByRole("form", { name: /Generate new enrollment tokens/i })).toBeVisible();

  const mobileBanner = await page
    .getByRole("banner", { name: "navigation" })
    .getByRole("button", { name: /menu/i })
    .isVisible();
  // eslint-disable-next-line playwright/no-conditional-in-test
  if (mobileBanner) {
    await page.getByRole("banner", { name: "navigation" }).getByRole("button", { name: /menu/i }).click();
  } else {
    await page.getByRole("banner", { name: /main/i }).hover();
  }
  await page.getByRole("banner", { name: /main/i }).getByRole("link", { name: /Sites/ }).click();

  await page.goBack();
  // eslint-disable-next-line playwright/no-wait-for-selector
  await page.waitForSelector('form[aria-label="Generate tokens"]', { state: "detached" });
});

test("closes and clears the form after creating the token", async ({ page }) => {
  await page.getByRole("button", { name: /Generate tokens/i }).click();
  await page.getByRole("textbox", { name: /Amount of tokens to generate/i }).type("1");
  await page.getByRole("textbox", { name: /Expiration time/i }).type("1 week");
  await page
    .getByRole("form", { name: /Generate new enrollment tokens/i })
    .getByRole("button", { name: /Generate 1 token/i })
    .click();
  await page.waitForResponse((resp) => resp.url().includes("/tokens") && resp.status() === 200);
  // eslint-disable-next-line playwright/no-wait-for-selector
  await page.waitForSelector('form[aria-label="Generate tokens"]', { state: "detached" });
  // check that the form has been reset
  await page.getByRole("button", { name: /Generate tokens/i }).click();
  await expect(
    page
      .getByRole("form", { name: /Generate new enrollment tokens/i })
      .getByRole("button", { name: /Generate 0 tokens/i }),
  ).toBeDisabled();
});

test("saves tokens to a file on export", async ({ page }) => {
  const [download] = await Promise.all([
    page.waitForEvent("download"),
    page.getByRole("button", { name: /Export/i }).click(),
  ]);
  const path = await download.path();
  const filename = await download.suggestedFilename();
  expect(filename).toMatch(/tokens.csv/);
  // verify that the file is saved to disk
  expect(fs.existsSync(path!)).toBeTruthy();
  // verify that the file is a valid csv
  const stream = await download.createReadStream();
  let data = "";
  for await (const chunk of stream!) {
    data += chunk;
  }
  const lines = data.split("\n");
  expect(lines[0]).toMatch(/id,value,expired,created/);
});
