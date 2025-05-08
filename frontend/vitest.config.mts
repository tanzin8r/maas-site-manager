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
      // exclude mock Resolvers:https://github.com/mswjs/msw/discussions/942#discussioncomment-1485279
      exclude: [
        ...coverageConfigDefaults.exclude,
        "**/index.ts",
        "src/mocks/**/*",
        "src/routes/**/*",
        "**/types.ts",
        "src/api/client/**/*",
        "src/apiclient/**/*",
        "src/testing/resolvers/**/*",
      ],
      include: ["src/**/*.{ts,tsx}"],
      reporter: [["text"], ["html"], ["cobertura", { file: "../../.cover/cobertura-coverage-frontend.xml" }]],
      thresholds: {
        lines: 80,
        functions: 80,
        // FIXME: temporarily lowered to 75 to get istanbulJS mergerd
        // should be bumped to 80
        branches: 75,
        statements: 80,
      },
      provider: "istanbul",
    },
    clearMocks: true,
  },
});
