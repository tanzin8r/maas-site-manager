import { test, expect } from "@playwright/test";

import { adminAuthFile } from "./constants";
import { routesConfig } from "@/config/routes";

test.use({ storageState: adminAuthFile });

test.beforeEach(async ({ page }) => {
  await page.goto(routesConfig.users.path);
});

test("can open and close the 'Add user' form", async ({ page }) => {
  await page.getByRole("button", { name: "Add user" }).click();
  await expect(page.getByRole("form", { name: "Add user" })).toBeVisible();

  await page.getByRole("button", { name: "Cancel" }).click();
  await expect(page.getByRole("form", { name: "Add user" })).toBeHidden();
});

test("can open and close the 'Edit user' form", async ({ page }) => {
  const rows = page.getByRole("rowgroup");
  const rowToEdit = rows.nth(1).getByRole("row").nth(0);
  const formTitle = await rowToEdit.getByRole("cell").nth(0).textContent();

  await rowToEdit.getByRole("button", { name: `Edit ${formTitle}` }).click();
  await expect(page.getByRole("form", { name: `Edit ${formTitle}` })).toBeVisible();

  await page.getByRole("button", { name: "Cancel" }).click();
  await expect(page.getByRole("form", { name: `Edit ${formTitle}` })).toBeHidden();
});

test("can open and close the 'Delete user' form", async ({ page }) => {
  const rows = page.getByRole("rowgroup");
  const rowToDelete = rows.nth(1).getByRole("row").nth(0);
  const formTitle = await rowToDelete.getByRole("cell").nth(0).textContent();

  await rowToDelete.getByRole("button", { name: `Delete ${formTitle}` }).click();
  await expect(page.getByRole("form", { name: `Delete ${formTitle}` })).toBeVisible();

  await page.getByRole("button", { name: "Cancel" }).click();
  await expect(page.getByRole("form", { name: `Delete ${formTitle}` })).toBeHidden();
});

test("can close forms using the escape key", async ({ page }) => {
  await page.getByRole("button", { name: "Add user" }).click();
  const form = page.getByRole("form", { name: "Add user" });
  await expect(page.getByRole("form", { name: "Add user" })).toBeVisible();

  await form.press("Escape");
  await expect(page.getByRole("form", { name: "Add user" })).toBeHidden();
});

test("closes the form after editing a user", async ({ page }) => {
  const rows = page.getByRole("rowgroup");
  const rowToEdit = rows.nth(1).getByRole("row").nth(0);
  const formTitle = await rowToEdit.getByRole("cell").nth(0).textContent();

  await rowToEdit.getByRole("button", { name: `Edit ${formTitle}` }).click();
  await expect(page.getByRole("form", { name: `Edit ${formTitle}` })).toBeVisible();

  await page.getByRole("textbox", { name: "Username" }).type("12345");
  await page.getByRole("button", { name: "Save" }).click();
  await expect(page.getByRole("form", { name: `Edit ${formTitle}` })).toBeHidden();
});

test("closes the form when navigating away", async ({ page }) => {
  await page.getByRole("button", { name: /Add user/i }).click();
  await expect(page.getByRole("form", { name: /Add user/i })).toBeVisible();

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
  await page
    .getByRole("navigation", { name: /main/i })
    .getByRole("link", { name: /Regions/ })
    .click();

  await page.goBack();
  await expect(page.getByRole("form", { name: /Add user/i })).toBeHidden();
});

test("can delete a user", async ({ page }) => {
  const testUsername = "Watto89";
  const dialog = page.getByRole("dialog", {
    name: /delete user/i,
  });
  await expect(dialog).toBeHidden();
  await page.getByRole("button", { name: new RegExp(`Delete ${testUsername}`, "i") }).click();
  await expect(dialog).toBeVisible();
  const deleteBtn = page.getByRole("button", { name: /^delete$/i });
  await expect(deleteBtn).toBeDisabled();
  await page.getByPlaceholder(testUsername).type(testUsername);
  await expect(deleteBtn).toBeEnabled();
  await deleteBtn.click();
  await expect(dialog).toBeHidden();
});
