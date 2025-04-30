import { defineConfig } from "@hey-api/openapi-ts";

export default defineConfig({
  input: `http://localhost:8000/api/openapi.json`,
  output: {
    path: "src/apiclient",
    format: "prettier",
    lint: "eslint",
  },
  plugins: [
    {
      name: "@hey-api/client-axios",
      runtimeConfigPath: "./src/hey-api.ts",
    },
    {
      enums: "typescript",
      name: "@hey-api/typescript",
    },
    "@hey-api/client-axios",
    "@hey-api/typescript",
    "@hey-api/sdk",
    "@tanstack/react-query",
  ],
});
