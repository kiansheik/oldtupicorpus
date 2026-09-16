import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "node:path";

const siteDir = process.env.SITE_DIR || "site";
const outDir = path.isAbsolute(siteDir) ? siteDir : `../${siteDir}`;

export default defineConfig({
  plugins: [react()],
  base: "./",
  build: {
    outDir,
    emptyOutDir: false,
  },
});
