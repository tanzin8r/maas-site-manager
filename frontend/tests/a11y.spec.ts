import { test, expect } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright"; // 1
import { protectedPages, publicPages } from "@/base/routesConfig";
import { adminAuthFile } from "./constants";

const a11yTest = async ({ title, path }: { title: string; path: string }) =>
  await test(`${title} page does not have any automatically detectable accessibility issues`, async ({ page }) => {
    // eslint-disable-next-line playwright/no-networkidle
    await page.goto(path, { waitUntil: "networkidle" });
    // verify the correct page has been displayed
    await expect(page).toHaveTitle(new RegExp(title));

    const accessibilityScanResults = await new AxeBuilder({ page })
      // @canonical/react-components Accordion is known to have accessibility issues
      .exclude(".p-accordion")
      .withTags(["wcag2a", "wcag2aa", "wcag21a", "wcag21aa"])
      .analyze();

    expect(accessibilityScanResults.violations).toEqual([]);
  });

test.describe("protected routes", () => {
  test.use({ storageState: adminAuthFile });
  Object.values(protectedPages).forEach(a11yTest);
});

test.describe("public routes", () => {
  Object.values(publicPages).forEach(a11yTest);
});
