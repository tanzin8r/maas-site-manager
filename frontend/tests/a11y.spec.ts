import { test, expect } from "@playwright/test";
import type { Page } from "@playwright/test";
import { AxeBuilder } from "@axe-core/playwright"; // 1
import { protectedPages, publicPages, routesConfig } from "@/config/routes";
import { adminAuthFile } from "./constants";

type ColorScheme = Pick<NonNullable<Parameters<Page["emulateMedia"]>[0]>, "colorScheme">["colorScheme"];
const a11yTest =
  (colorScheme: ColorScheme) =>
  async ({ title, path }: { title: string; path: string }) =>
    await test(`${title} page does not have any automatically detectable accessibility issues in ${colorScheme} mode`, async ({
      page,
    }) => {
      await page.emulateMedia({ colorScheme, reducedMotion: "reduce" });
      // eslint-disable-next-line playwright/no-networkidle
      await page.goto(path, {
        // map tends to trigger continuous network requests disallowing the use of networkidle
        waitUntil: path.includes(routesConfig.sitesMap.path) ? "domcontentloaded" : "networkidle",
      });
      // verify the correct page has been displayed
      await expect(page).toHaveTitle(new RegExp(title));

      const accessibilityScanResults = await new AxeBuilder({ page })
        // @canonical/react-components Accordion is known to have accessibility issues
        .exclude(".p-accordion")
        // TODO: https://warthogs.atlassian.net/browse/MAASENG-2043
        .withTags(["wcag2a", "wcag2aa", "wcag21a", "wcag21aa"])
        .analyze();

      expect(accessibilityScanResults.violations).toEqual([]);
    });

test.describe("protected routes", () => {
  test.use({ storageState: adminAuthFile });
  Object.values(protectedPages).forEach(a11yTest("light"));
  Object.values(protectedPages).forEach(a11yTest("dark"));
});

test.describe("public routes", () => {
  Object.values(publicPages).forEach(a11yTest("light"));
  Object.values(publicPages).forEach(a11yTest("dark"));
});
