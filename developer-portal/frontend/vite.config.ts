import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      "/api": {
        target: "http://localhost:8004",
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ""),
      },
      "/identity": {
        target: "http://localhost:8005",
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/identity/, ""),
      },
    },
  },
});
