import { configDefaults, coverageConfigDefaults, defineConfig } from "vitest/config";
import AutoImport from "unplugin-auto-import/vite";
import * as path from "path";

export default defineConfig({
  plugins: [
    AutoImport({
      imports: ["react", "vitest"],
      dts: true,
      eslintrc: {
        enabled: true,
      },
    }),
  ],
  resolve: {
    alias: { "@": path.resolve(__dirname, "src") },
  },
  test: {
    environment: "jsdom",
    server: {
      deps: {
        inline: ["vitest-canvas-mock"],
      },
    },
    setupFiles: ["./mock-web-worker.ts", "./setupTests.ts"],
    exclude: [...configDefaults.exclude, "**/tests/**"],
    coverage: {
      // exclude index files as they're only used to export other files
      // exclude pages as they're covered by playwright tests
      exclude: [
        ...coverageConfigDefaults.exclude,
        "**/index.ts",
        "src/mocks/**/*",
        "src/routes/**/*",
        "**/types.ts",
        "src/api/client/**/*",
      ],
      include: ["src/**/*.{ts,tsx}"],
      reporter: ["text", "json", "html"],
      thresholds: {
        lines: 80,
        functions: 80,
        branches: 80,
        statements: 80,
      },
    },
    clearMocks: true,
  },
});
