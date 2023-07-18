import { defineConfig } from "vite";
import react from "@vitejs/plugin-react-swc";
import AutoImport from "unplugin-auto-import/vite";
import stylelint from "vite-plugin-stylelint";
import autoprefixer from "autoprefixer";
import { config } from "dotenv";
import * as path from "path";

config({ path: "../.env" });

const commitHash = require("child_process").execSync("git rev-parse --short HEAD").toString();

// https://vitejs.dev/config/
export default defineConfig({
  envDir: "../",
  define: { "import.meta.env.VITE_APP_VERSION": JSON.stringify(commitHash) },
  plugins: [
    react(),
    AutoImport({
      imports: ["react", "vitest"],
      dts: true,
      eslintrc: {
        enabled: true,
      },
    }),
    stylelint(),
  ],
  css: {
    postcss: {
      plugins: [autoprefixer()],
    },
  },
  server: { port: Number(process.env.VITE_UI_PORT) },
  resolve: {
    alias: { "@": path.resolve(__dirname, "src") },
  },
});
