import { defineConfig } from "vite";
import react from "@vitejs/plugin-react-swc";
import dotenv from "dotenv";

dotenv.config({ path: "../.env" });

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: { port: Number(process.env.VITE_UI_PORT) },
});
