import { defineConfig } from "vite";
import react from "@vitejs/plugin-react-swc";
import AutoImport from "unplugin-auto-import/vite";
import stylelint from "vite-plugin-stylelint";
import dotenv from "dotenv";
import * as path from "path";

dotenv.config({ path: "../.env" });

const commitHash = require("child_process").execSync("git rev-parse --short HEAD").toString();

// https://vitejs.dev/config/
export default defineConfig({
  define: { "import.meta.env.VITE_APP_VERSION": JSON.stringify(commitHash) },
  plugins: [
    react(),
    AutoImport({
      imports: ["react", "react-router-dom", "vitest"],
      dts: true,
      eslintrc: {
        enabled: true,
      },
    }),
    stylelint(),
  ],
  server: { port: Number(process.env.VITE_UI_PORT) },
  resolve: {
    alias: { "@": path.resolve(__dirname, "src") },
  },
});
